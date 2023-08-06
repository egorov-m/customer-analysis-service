import logging as log

from random import randint
from time import sleep

from geopy import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from sqlalchemy import or_, not_
from sqlmodel import Session, select

from cas_worker.db.models import Customer, RegionalLocation


class Preparer:
    """
    Data preparer base class
    """

    logger = log.getLogger('analysis_preparer_logger')

    def __init__(self, session: Session):
        self.session = session
        self.user_agent = 'user_me_{}'.format(randint(10000, 99999))
        self.geolocator = Nominatim(user_agent=self.user_agent)

    def geocode(self, location: str, sleep_sec):
        try:
            return self.geolocator.geocode(location)
        except GeocoderTimedOut:
            self.logger.info('TIMED OUT: GeocoderTimedOut: Retrying...')
            sleep(randint(1 * 100, sleep_sec * 100) / 100)
            return self.geocode(location, sleep_sec)
        except GeocoderServiceError as e:
            self.logger.info('CONNECTION REFUSED: GeocoderServiceError encountered.')
            self.logger.error(e)
            return None
        except Exception as e:
            self.logger.info('ERROR: Terminating due to exception {}'.format(e))
            return None

    def fill_table_regional_locations(self):
        self.logger.info('Start fill table regional locations')
        with self.session as session:
            current_set_customer_regions = session.exec(select(Customer.country_ru,
                                                               Customer.country_en,
                                                               Customer.city_ru,
                                                               Customer.city_en)
                                                        .distinct()
                                                        .where(or_(Customer.country_ru.isnot(None),
                                                                   Customer.city_ru.isnot(None)))).all()
            self.logger.info('Got the current set of regions of all customers')
            for customer_region in current_set_customer_regions:
                if customer_region['country_ru'] is None and customer_region['city_ru'] is None:
                    continue
                if customer_region['country_ru'] is None:
                    regionals_locations: list[RegionalLocation] = session.exec(select(RegionalLocation)
                                                                               .where(RegionalLocation.city_ru == customer_region['city_ru'])
                                                                               .where(not_(Customer.country_ru.isnot(None)))).all()
                    if len(regionals_locations) > 0:
                        continue
                    else:
                        location = self.geocode(customer_region['city_en'], 2)
                        if location is None:
                            continue
                        _add_regionals_locations(session, customer_region, location)
                elif customer_region['city_ru'] is None:
                    regionals_locations: list[RegionalLocation] = session.exec(select(RegionalLocation)
                                                                               .where(RegionalLocation.country_ru == customer_region['country_ru'])
                                                                               .where(not_(Customer.city_ru.isnot(None)))).all()
                    if len(regionals_locations) > 0:
                        continue
                    else:
                        location = self.geocode(customer_region['country_en'], 2)
                        if location is None:
                            continue
                        _add_regionals_locations(session, customer_region, location)
                else:
                    regionals_locations: list[RegionalLocation] = session.exec(select(RegionalLocation)
                                                                               .where(RegionalLocation.country_ru == customer_region['country_ru'])
                                                                               .where(RegionalLocation.city_ru == customer_region['city_ru'])).all()
                    if len(regionals_locations) > 0:
                        continue
                    else:
                        location = self.geocode(f'{customer_region["country_en"]}, {customer_region["city_en"]}', 2)
                        if location is None:
                            continue
                        _add_regionals_locations(session, customer_region, location)

                self.logger.info(f'Executed: {customer_region["country_en"]}, {customer_region["city_en"]}: {location.latitude} | {location.longitude}')

        self.logger.info('Fill table regional locations completed.')


def _add_regionals_locations(session: Session, customer_region, location):
    regional_location: RegionalLocation = RegionalLocation()
    regional_location.country_ru = customer_region['country_ru']
    regional_location.country_en = customer_region['country_en']
    regional_location.city_ru = customer_region['city_ru']
    regional_location.city_en = customer_region['city_en']
    regional_location.latitude = location.latitude
    regional_location.longitude = location.longitude
    session.add(regional_location)
    session.commit()
