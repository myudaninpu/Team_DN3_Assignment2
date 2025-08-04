import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import csv
import datetime

# Define pipeline options
options = PipelineOptions(
    runner='DataflowRunner',
    project='mgmt599-kyashawilliams-lab2',  # Replace with your GCP project ID
    region='us-central1',
    temp_location='gs://kyashawilliams-assignment2-kaggle-store-sales/temp',  # Replace with your bucket name
    staging_location='gs://kyashawilliams-assignment2-kaggle-store-sales/staging'
)

def parse_oil_record(record):
    """
    Parses a CSV record from the oil data.
    Returns a dictionary or None if parsing fails.
    """
    try:
        # Malformed rows might not have 2 columns.
        if len(record) != 2:
            return None
        
        # The dcoilwtico value can be '.' for missing data.
        price = float(record[1]) if record[1] != '.' else None
        
        return {
            'date': datetime.datetime.strptime(record[0], '%Y-%m-%d').date(),
            'dcoilwtico': price
        }
    except (ValueError, TypeError):
        # Catches errors from float(), strptime(), etc.
        return None

def parse_train_record(record):
    """
    Parses a CSV record from the train data.
    Returns a dictionary or None if parsing fails.
    """
    try:
        # Malformed rows might not have 6 columns.
        if len(record) != 6:
            return None
        return {
            'id': int(record[0]),
            'date': datetime.datetime.strptime(record[1], '%Y-%m-%d').date(),
            'store_nbr': int(record[2]),
            'family': record[3],
            'sales': float(record[4]),
            'onpromotion': int(record[5])
        }
    except (ValueError, TypeError):
        # Catches errors from int(), float(), strptime(), etc.
        return None

class CalculateDailySales(beam.DoFn):
    """Calculates daily sales statistics from grouped sales records."""
    def process(self, element):
        date, records = element
        records_list = list(records)

        total_sales = sum(r['sales'] for r in records_list)
        stores_active = len(set(r['store_nbr'] for r in records_list))
        onpromotion_values = [r['onpromotion'] for r in records_list]
        avg_promo_items = (sum(onpromotion_values) / len(onpromotion_values)
                           if onpromotion_values else 0.0)

        yield {
            'date': date,
            'total_sales': total_sales,
            'stores_active': stores_active,
            'avg_promo_items': avg_promo_items
        }

class FormatJoinedData(beam.DoFn):
    """
    Formats the co-grouped data for BigQuery.
    This performs a left join of daily_sales with oil_prices.
    """
    def process(self, element):
        date, data = element
        daily_sales_records = data['daily_sales']
        oil_price_records = data['oil_prices']

        if not daily_sales_records:
            return

        sales_record = daily_sales_records[0]
        oil_price = oil_price_records[0]['dcoilwtico'] if oil_price_records else None

        output_record = sales_record.copy()
        output_record['dcoilwtico'] = oil_price
        yield output_record

# Define the pipeline
def run():
    with beam.Pipeline(options=options) as pipeline:
        # Branch 1: Read, transform, and load stores data. This is independent.
        (
            pipeline
            | 'ReadStoresFromGCS' >> beam.io.ReadFromText('gs://kyashawilliams-assignment2-kaggle-store-sales/stores.csv', skip_header_lines=1)
            | 'ParseStoresCSV' >> beam.Map(lambda line: next(csv.reader([line])))
            | 'TransformStoresData' >> beam.Map(lambda record: {
                'store_nbr': int(record[0]),
                'city': record[1],
                'state': record[2],
                'type': record[3],
                'cluster': int(record[4])
            })
            | 'WriteStoresToBigQuery' >> beam.io.WriteToBigQuery(
                'mgmt599-kyashawilliams-lab2.assignment2_storesales.stores',
                schema='store_nbr:INTEGER, city:STRING, state:STRING, type:STRING, cluster:INTEGER',
                write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE
            )
        )

        # Branch 2: Read oil data, load to BigQuery, and prepare for join.
        oil_pcoll = (
            pipeline
            | 'ReadOilFromGCS' >> beam.io.ReadFromText('gs://kyashawilliams-assignment2-kaggle-store-sales/oil.csv', skip_header_lines=1)
            | 'ParseOilCSV' >> beam.Map(lambda line: next(csv.reader([line])))
            | 'ParseAndFilterOil' >> beam.Map(parse_oil_record)
            | 'FilterBadOilRecords' >> beam.Filter(lambda x: x is not None)
        )

        # Sink 2a: Write raw oil data to BigQuery.
        (oil_pcoll
            | 'WriteOilToBigQuery' >> beam.io.WriteToBigQuery(
                'mgmt599-kyashawilliams-lab2.assignment2_storesales.oil',
                schema='date:DATE, dcoilwtico:FLOAT',
                write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE
            )
        )

        # Prepare oil data for join by keying on date.
        oil_for_join = oil_pcoll | 'KeyOilByDate' >> beam.Map(lambda row: (row['date'], row))

        # Branch 3: Read train data, load to BigQuery, and aggregate for join.
        transformed_train_data = (
            pipeline
            | 'ReadTrainFromGCS' >> beam.io.ReadFromText('gs://kyashawilliams-assignment2-kaggle-store-sales/train.csv', skip_header_lines=1)
            | 'ParseTrainCSV' >> beam.Map(lambda line: next(csv.reader([line])))
            | 'ParseAndFilterTrain' >> beam.Map(parse_train_record)
            | 'FilterBadTrainRecords' >> beam.Filter(lambda x: x is not None)
        )

        # Sink 3a: Write raw training data to BigQuery.
        (
            transformed_train_data
            | 'WriteTrainToBigQuery' >> beam.io.WriteToBigQuery(
                'mgmt599-kyashawilliams-lab2.assignment2_storesales.train',
                schema='id:INTEGER, date:DATE, store_nbr:INTEGER, family:STRING, sales:FLOAT, onpromotion:INTEGER',
                write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE
            )
        )

        # Sink 3b: Aggregate sales data and prepare for join.
        daily_sales_for_join = (
            transformed_train_data
            | 'FilterTrainingData' >> beam.Filter(lambda row: row['date'] < datetime.date(2017, 8, 1))
            | 'MapDateToData' >> beam.Map(lambda row: (row['date'], {'sales': row['sales'], 'store_nbr': row['store_nbr'], 'onpromotion': row['onpromotion']}))
            | 'GroupByDate' >> beam.GroupByKey()
            | 'CalculateDailyStats' >> beam.ParDo(CalculateDailySales())
            | 'KeyDailySalesByDate' >> beam.Map(lambda row: (row['date'], row))
        )

        # Branch 4: Join aggregated sales with oil data and write to a features table.
        (
            {'daily_sales': daily_sales_for_join, 'oil_prices': oil_for_join}
            | 'JoinSalesAndOil' >> beam.CoGroupByKey()
            | 'FormatJoinedData' >> beam.ParDo(FormatJoinedData())
            | 'WriteDailyFeaturesToBigQuery' >> beam.io.WriteToBigQuery(
                'mgmt599-kyashawilliams-lab2.assignment2_storesales.daily_features',
                schema='date:DATE, total_sales:FLOAT, stores_active:INTEGER, avg_promo_items:FLOAT, dcoilwtico:FLOAT',
                write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE
            )
        )

if __name__ == '__main__':
    run()
