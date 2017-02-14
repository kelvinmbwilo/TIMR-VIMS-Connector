import sys
import requests
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from requests.auth import HTTPBasicAuth

vims_username = ''
vims_password = ''
timr_username = ''
timr_password = ''
timr_server = ''
vims_server = ""

def get_server_request(url):
    r = requests.get(vims_server + url, auth=HTTPBasicAuth(vims_username, vims_password))
    if r.status_code == 200:
        return r.json()
    else:
        return 'error'


def get_timr_server_request(url):
    r = requests.get(timr_server + url, auth=(timr_username, timr_password), verify='cacert.cer')
    if r.status_code == 200:
        return r.json()
    else:
        return "error"


# data mapping
facility_mapping = [
  {
    "name": "Ngarenaro UHC ",
    "vims_id": "16451",
    "timr_id": "16321"
  }
]

vaccine_mapping = [
    {
        'name': 'BCG',
        'vims_id': '2412',
        'timr_name': 'BCG',
        'code': 'VOO1',
        'display_order': '1',
        'category': 'Vaccine'
    }, {
        'name': 'BCG diluent',
        'vims_id': '2434',
        'timr_name': 'BCG',
        'code': '',
        'display_order': '',
        'category': 'Vaccine'
    }, {
        'name': 'OPV',
        'vims_id': '2413',
        'timr_name': 'OPV',
        'code': 'VOO2',
        'display_order': '2',
        'category': 'Vaccine'
    }, {
        'name': 'PCV-13',
        'vims_id': '2415',
        'timr_name': 'PCV-13',
        'code': 'VOO4',
        'display_order': '4',
        'category': 'Vaccine'
    }, {
        'name': 'DTP-HepB-Hib',
        'vims_id': '2421',
        'timr_name': 'DTP-HepB-Hib',
        'code': 'VO10',
        'display_order': '5',
        'category': 'Vaccine'
    }, {
        'name': 'Rota',
        'vims_id': '2416',
        'timr_name': 'Rota',
        'code': 'V005',
        'display_order': '6',
        'category': 'Vaccine'
    }, {
        'name': 'Measles Rubella',
        'vims_id': '2420',
        'timr_name': 'Measles Rubella',
        'code': 'V009',
        'display_order': '7',
        'category': 'Vaccine'
    }, {
        'name': 'Tetanus Toxoide',
        'vims_id': '2418',
        'timr_name': 'Tetanus Toxoid',
        'code': 'V007',
        'display_order': '9',
        'category': 'Vaccine'
    }, {
        'name': 'ADS_0.05ml',
        'vims_id': '2422',
        'timr_name': 'ADS_005ML',
        'code': 'ADS_0.05ml',
        'display_order': '21',
        'category': 'Syringes and safety boxes'
    }, {
        'name': 'ADS_0.5ml',
        'vims_id': '2423',
        'timr_name': 'ADS_05ML',
        'code': 'V011',
        'display_order': '22',
        'category': 'Syringes and safety boxes'
    }, {
        'name': 'Sdilution_5ml',
        'vims_id': '2425',
        'timr_name': 'SDILLUTION',
        'code': 'V014',
        'display_order': '23',
        'category': 'Syringes and safety boxes'
    }, {
        'name': 'Safety boxes',
        'vims_id': '2426',
        'timr_name': 'SAFETY_BOXES',
        'code': 'V015',
        'display_order': '24',
        'category': 'Syringes and safety boxes'
    }, {
        'name': 'Vit. A 200000 IU',
        'vims_id': '2431',
        'timr_name': 'VITAMIN_A_200000_IU',
        'code': 'V019',
        'display_order': '51',
        'category': 'Vitamins'
    }, {
        'name': 'Vit. A 100000 IU',
        'vims_id': '2430',
        'timr_name': 'VITAMIN_A_100000_IU',
        'code': 'V018',
        'display_order': '50',
        'category': 'Vitamins'
    }
]

doses_mapping = [
    {
        'name': 'Dose 0',
        'vims_id': '1',
        'timr_id': '0'
    },{
        'name': 'Dose 1',
        'vims_id': '1',
        'timr_id': '1'
    }, {
        'name': 'Dose 2',
        'vims_id': '2',
        'timr_id': '2'
    }, {
        'name': 'Dose 3',
        'vims_id': '3',
        'timr_id': '3'
    }, {
        'name': 'Dose 4',
        'vims_id': '4',
        'timr_id': '4'
    }, {
        'name': 'Dose 5',
        'vims_id': '5',
        'timr_id': '5'
    }, {
        'name': 'Completed TT',
        'vims_id': '6',
        'timr_id': '6'
    }
]

deseas_mapping = [
    {
        'name': 'Fever and rash illness',
        'id': '1',
        'timr_death_name': 'FeverMonthlyDeaths',
        'timr_case_name': 'FeverMonthlyCases'
    },
    {
        'name': 'AFP Cases',
        'id': '2',
        'timr_death_name': 'AFPDeaths',
        'timr_case_name': 'AFPMonthlyCases'
    },
    {
        'name': 'Neonatal Tetanus',
        'id': '3',
        'timr_case_name': 'NeonatalTTCases',
        'timr_death_name': 'NeonatalTTDeaths'
    }
]


def get_doses_from_mapping(timr_id):
    for dose in doses_mapping:
        if dose['timr_id'] == timr_id:
            return dose


def get_vaccine_from_mapping(timr_name):
    for vaccine in vaccine_mapping:
        if vaccine['timr_name'] == timr_name:
            return vaccine

# use this for testing 16300
facilityID = '16451'

# get available periods for a facility
periods_with_reports = get_server_request("rest-api/ivd/periods/"+facilityID+"/82")

# Returns the same day of last month if possible otherwise end of month
# (eg: March 31st->29th Feb an July 31st->June 30th)
last_month = datetime.now() - relativedelta(months=1)
current_month = datetime.now()
# Create string of month name and year...
last_month_text = format(last_month, '%b %Y')
current_month_text = format(current_month, '%b %Y')


def checkIfReportIsAvailable():
    check = False
    if periods_with_reports != 'error':
        for report in periods_with_reports['periods']:
            if report['status'] == 'DRAFT':
                check = True
    return check


def getMonthlyReport():
    selected_report = {}
    for report in periods_with_reports['periods']:
        if report['status'] == 'DRAFT':
            selected_report = report
    return selected_report


def preparePeriodRange(period):
    month = period[:4]
    year = period[5:]
    return_period = {}
    if month == "Jan":
        return_period['start'] = year+"-01-01"
        return_period['end'] = year+"-01-31"
    if month == "Feb":
        return_period['start'] = year+"-02-01"
        return_period['end'] = year+"-02-28"
    if month == "Mar":
        return_period['start'] = year+"-03-01"
        return_period['end'] = year+"-03-31"
    if month == "Apr":
        return_period['start'] = year+"-04-01"
        return_period['end'] = year+"-04-31"
    if month == "May":
        return_period['start'] = year+"-05-01"
        return_period['end'] = year+"-05-30"
    if month == "June":
        return_period['start'] = year+"-06-01"
        return_period['end'] = year+"-06-30"
    if month == "July":
        return_period['start'] = year+"-07-01"
        return_period['end'] = year+"-07-31"
    if month == "Aug":
        return_period['start'] = year+"-08-01"
        return_period['end'] = year+"-08-31"
    if month == "Sept":
        return_period['start'] = year+"-09-01"
        return_period['end'] = year+"-09-30"
    if month == "Oct":
        return_period['start'] = year+"-01-01"
        return_period['end'] = year+"-10-31"
    if month == "Nov":
        return_period['start'] = year+"-11-01"
        return_period['end'] = year+"-11-30"
    if month == "Dec":
        return_period['start'] = year+"-12-01"
        return_period['end'] = year+"-12-31"
    return return_period


def prepareOtherPeriodRange(period):
    month = period[:4]
    year = period[5:]
    return_period = {}
    if month == "Jan":
        return_period['reportingMonth'] = "01"
    if month == "Feb":
        return_period['reportingMonth'] = "02"
    if month == "Mar":
        return_period['reportingMonth'] = "03"
    if month == "Apr":
        return_period['reportingMonth'] = "04"
    if month == "May":
        return_period['reportingMonth'] = "05"
    if month == "June":
        return_period['reportingMonth'] = "06"
    if month == "July":
        return_period['reportingMonth'] = "07"
    if month == "Aug":
        return_period['reportingMonth'] = "08"
    if month == "Sept":
        return_period['reportingMonth'] = "09"
    if month == "Oct":
        return_period['reportingMonth'] = "01"
    if month == "Nov":
        return_period['reportingMonth'] = "11"
    if month == "Dec":
        return_period['reportingMonth'] = "12"

    return_period['reportingYear'] = year
    return return_period

# this variable will hold the bolean value that check if the report is available or not
report_is_available = checkIfReportIsAvailable()
print report_is_available
monthly_report = None
if report_is_available:
    # get the report sturcture
    report = getMonthlyReport()
    print report
    monthly_report = get_server_request("rest-api/ivd/get/"+str(report['id'])+".json")
    print monthly_report['report']['plannedOutreachImmunizationSessions']
    basic_period = preparePeriodRange(monthly_report['report']['period']['name'])
    other_period = prepareOtherPeriodRange(monthly_report['report']['period']['name'])
    for facility in facility_mapping:
        period_id = report['periodId']
        print facility['name']
        print period_id
        report_basis = get_timr_server_request(
            'SVC/HealthFacilityManagement.svc/GetHealthFacilityImmunizationSessions?healthFacilityId=' + facility[
                'timr_id'] + '&reportingMonth='+other_period['reportingMonth']+'&reportingYear='+other_period['reportingYear'])
        if len(report_basis) != 0:
            sessions = {'majorImmunizationActivities': str(report_basis[0]['OtherMajorImmunizationActivities']),
                        'fixedImmunizationSessions': str(report_basis[0]['FixedConducted']),
                        'plannedOutreachImmunizationSessions': str(report_basis[0]['OutreachPlanned']),
                        'outreachImmunizationSessions': str(report_basis[0]['OutreachConducted']),
                        'outreachImmunizationSessionsCanceled': str(report_basis[0]['OutreachCanceled'])
                        }
        else:
            sessions = {'majorImmunizationActivities': '0',
                        'fixedImmunizationSessions': '0',
                        'plannedOutreachImmunizationSessions': '0',
                        'outreachImmunizationSessions': '0',
                        'outreachImmunizationSessionsCanceled': '0'
                        }
        if sessions['majorImmunizationActivities'] == "":
            sessions['majorImmunizationActivities'] = '0'

        monthly_report['report']['plannedOutreachImmunizationSessions'] = sessions['plannedOutreachImmunizationSessions']
        monthly_report['report']['majorImmunizationActivities'] =  sessions['majorImmunizationActivities']
        monthly_report['report']['outreachImmunizationSessions'] = sessions['outreachImmunizationSessions']
        monthly_report['report']['fixedImmunizationSessions'] = sessions['fixedImmunizationSessions']
        monthly_report['report']['outreachImmunizationSessionsCanceled'] = sessions['outreachImmunizationSessionsCanceled']

        # get survilience info:
        vaccinations = get_timr_server_request(
            'SVC/HealthFacilityManagement.svc/GetHealthFacilityVaccinations?healthFacilityId=' + facility[
                'timr_id'] + '&fromDate='+basic_period['start']+'&toDate='+basic_period['end'])

        vitamin_stock = get_timr_server_request(
            'SVC/HealthFacilityManagement.svc/GetHealthFacilityVitaminAStockBalance?healthFacilityId=' + facility[
                'timr_id'] + '&reportingMonth='+other_period['reportingMonth']+'&reportingYear='+other_period['reportingYear'])
        #
        safety_stock = get_timr_server_request(
            'SVC/HealthFacilityManagement.svc/GetHealthFacilitySyringesAndSafetyBoxesStockBalance?healthFacilityId=' +
            facility['timr_id'] + '&reportingMonth='+other_period['reportingMonth']+'&reportingYear='+other_period['reportingYear'])
        #
        vaccine_stock = get_timr_server_request(
            'SVC/StockManagement.svc/GetHealthFacilityCurrentStockByDose?hfid=' + facility[
                'timr_id'] + '&fromDate='+basic_period['start']+'&toDate='+basic_period['end'])
        #
        deseases = get_timr_server_request(
            'SVC/HealthFacilityManagement.svc/GetHealthFacilityDeseaseSurvailance?healthFacilityId=' + facility[
                'timr_id'] + '&reportingMonth='+other_period['reportingMonth']+'&reportingYear='+other_period['reportingYear'])

        vitamina = get_timr_server_request(
            'SVC/HealthFacilityManagement.svc/GetChildSupplementsByChild?healthFacilityId=' + facility[
                'timr_id'] + '&fromTime='+basic_period['start']+'&toTime='+basic_period['end'])

        # proceccing vitamin A
        vitamin_count = 0
        for vit in monthly_report['report']['vitaminSupplementationLineItems']:
            if vit['ageGroup'] == '9 Months':
                monthly_report['report']['vitaminSupplementationLineItems'][vitamin_count]['femaleValue'] = vitamina[
                    'female9Months']
                monthly_report['report']['vitaminSupplementationLineItems'][vitamin_count]['maleValue'] = vitamina[
                    'male9Months']
            if vit['ageGroup'] == '15 Months':
                monthly_report['report']['vitaminSupplementationLineItems'][vitamin_count]['femaleValue'] = vitamina[
                    'female15Months']
                monthly_report['report']['vitaminSupplementationLineItems'][vitamin_count]['maleValue'] = vitamina[
                    'male15Months']
            if vit['ageGroup'] == '18 Months':
                monthly_report['report']['vitaminSupplementationLineItems'][vitamin_count]['femaleValue'] = vitamina[
                    'female18Months']
                monthly_report['report']['vitaminSupplementationLineItems'][vitamin_count]['maleValue'] = vitamina[
                    'male18Months']
            vitamin_count += 1

        deseas_count = 0
        for des in monthly_report['report']['diseaseLineItems']:
            for deseas in deseases:
                for mapping in deseas_mapping:
                    if mapping['name'] == des['diseaseName']:
                        monthly_report['report']['diseaseLineItems'][deseas_count]['cases'] = deseas[
                            mapping['timr_case_name']]
                        monthly_report['report']['diseaseLineItems'][deseas_count]['death'] = deseas[
                            mapping['timr_death_name']]
            deseas_count += 1
        f = open('dataValues_.json', 'w')
        f.write(json.dumps(monthly_report))
        exit()
        for vacinnate in vaccinations['healthFacilityVaccinations']:
            immunization = {}
            product = get_vaccine_from_mapping(vacinnate['antigen'])
            print vacinnate['antigen']
            print "*******"
            print product
            dose = get_doses_from_mapping(str(vacinnate['dose']))
            if dose:
                immunization['displayName'] = dose['name']
                immunization['displayOrder'] = dose['vims_id']
                immunization['regularMale'] = str(vacinnate['serviceAreaMale'])
                immunization['regularFemale'] = str(vacinnate['serviceAreaFemale'])
                immunization['outreachMale'] = str(vacinnate['catchmentMale'])
                immunization['outreachFemale'] = str(vacinnate['catchmentFemale'])

        for deseas in deseases:
            for mapping in deseas_mapping:
                desease_details = {'diseaseName': mapping['name'],
                                   'displayOrder': mapping['id'],
                                   'cases': str(deseas[mapping['timr_case_name']]),
                                   'death': str(deseas[mapping['timr_death_name']]),
                                   'cumulative': str(
                                       deseas[mapping['timr_case_name']] + deseas[mapping['timr_death_name']])
                                   }

        for stock in vaccine_stock:
            use_vaccine = get_vaccine_from_mapping(stock['antigen'])
            logistics = {'productCode': use_vaccine['code'],
                         'productName': use_vaccine['name'],
                         'productCategory': use_vaccine['category'],
                         'displayOrder': use_vaccine['display_order'],
                         'quantityReceived': str(stock['dosesReceived']),
                         'closingBalance': str(stock['stockOnHand']),
                         'quantityDiscardedUnopened': str(stock['dosesDiscardedUnopened']),
                         'quantityDiscardedOpened': '0',
                         'daysStockedOut': '0',
                         'quantityIssued': str(stock['dosesDiscardedOpened']),
                         'quantityVvmAlerted': '0',
                         'quantityFreezed': '0',
                         'quantityExpired': '0',
                         'quantityWastedOther': '0',
                         'discardingReasonId': 'null',
                         'discardingReasonExplanation': ' '
                         }

        for stock in safety_stock:
            use_vaccine = get_vaccine_from_mapping(stock['ItemName'])
            logistics = {'productCode': use_vaccine['code'],
                         'productName': use_vaccine['name'],
                         'productCategory': use_vaccine['category'],
                         'displayOrder': use_vaccine['display_order'],
                         'quantityReceived': str(stock['Received']),
                         'closingBalance': str(stock['StockInHand']),
                         'quantityDiscardedUnopened': '0',
                         'quantityDiscardedOpened': '0',
                         'daysStockedOut': str(stock['StockedOutDays']),
                         'quantityIssued': str(stock['Used']),
                         'quantityVvmAlerted': '0',
                         'quantityFreezed': '0',
                         'quantityExpired': '0',
                         'quantityWastedOther': '0',
                         'discardingReasonId': 'null',
                         'discardingReasonExplanation': ' '
                         }

        for stock in vitamin_stock:
            use_vaccine = get_vaccine_from_mapping(stock['VitaminName'])
            logistics = {'productCode': use_vaccine['code'],
                         'productName': use_vaccine['name'],
                         'productCategory': use_vaccine['category'],
                         'displayOrder': use_vaccine['display_order'],
                         'quantityReceived': str(stock['Received']),
                         'closingBalance': str(stock['StockInHand']),
                         'quantityDiscardedUnopened': '0',
                         'quantityDiscardedOpened': '0',
                         'daysStockedOut': '0',
                         'quantityIssued': str(stock['TotalAdministered']),
                         'quantityVvmAlerted': '0',
                         'quantityFreezed': '0',
                         'quantityExpired': '0',
                         'quantityWastedOther': '0',
                         'discardingReasonId': 'null',
                         'discardingReasonExplanation': ' '
                         }




