import time
import os
import math
from scipy import stats


def read_dates(dates_file):
    '''reads the input csv file with RC determinations and returns
    a list of means and a list of standard deviations'''

    datesDict = {}
    meanList = []
    stDevList = []
    phasesDict = {}

    infile = open(dates_file)
    line = infile.readline()
    count = 0
    ID_pos = None
    date_pos = None
    sigma_pos = None
    phase_pos = None
    phase_specified = True
    while line:
        lineList = line.split(',')
        lineList = [x.strip() for x in lineList]

        if count == 0:  # first line is header
            for el in enumerate(lineList):
                pos = el[0]
                val = el[1].strip().lower()

                if val == 'id':
                    ID_pos = pos
                elif val == 'date':
                    date_pos = pos
                elif val == 'sigma':
                    sigma_pos = pos
                elif val == 'phase':
                    phase_pos = pos

            if (ID_pos is None) or (date_pos is None) or (sigma_pos is None):
                infile.close()
                raise Exception('Unable to find either id, date or sigma csv headers')
            if phase_pos is None:
                phase_specified = False

        else:
            dateID = int(lineList[ID_pos])
            date = lineList[date_pos]
            sigma = lineList[sigma_pos]
            phaseID = 1
            if phase_specified == True:
                phaseID = lineList[phase_pos]

            mean = int(date)
            meanList.append(mean)

            stDev = int(sigma)
            stDevList.append(stDev)

            datesDict[dateID] = (mean, stDev)

            if phaseID in phasesDict:
                phasesDict[phaseID].append(dateID)
            else:
                phasesDict[phaseID] = [dateID]

        line = infile.readline()
        count += 1
    infile.close()
    return datesDict, phasesDict


def save_std_out(output_folder, std_out):
    '''returns a .txt file with test results'''

    outfile_path = os.path.join(output_folder, 'results.txt')
    with open(outfile_path, 'w') as fw:
        fw.write(std_out)


description = {
    "title": "Ward and Wilson Test",
    "slug": "ward_and_wilson_test",
    "version": "1.2",
    "authors": [
        {
            "name": "Federico Antolini",
            "url": "",
            "info": "...",
            "email": "federico-antolini@uiowa.edu"
        },
        {
            "name": "Tiziano Fantuzzi",
            "url": "mailto:tiziano.fantuzzi@gmail.com",
            "info": "...",
            "email": "..."
        }
    ],
    "description": "...",
    "parameters": [
        {
            "key": "confidence_level",
            "name": "Confidence level",
            "description": "...",
            "type": "integer",
            "default": 0,
            "maxlength": 2
        }
    ],
    "required_dataset_fields": [
        "ID",
        "date",
        "sigma"
    ],
    "optional_dataset_fields": []
}


def generate_output(test_statistics, pooled_mean, pooled_stDev, confidence_level, thresholds):
    if confidence_level == 0:
        confidence_levels = [90, 95, 99]
        for i, level in enumerate(confidence_levels):
            if test_statistics < thresholds[i]:
                return (f"Test passed at confidence level of {level}%\n"
                        f"RC determinations may refer to the same date\n\n"
                        f"Best estimated date: {pooled_mean} +/- {pooled_stDev}\n"
                        f"Pooled mean: {pooled_mean}\n"
                        f"Pooled sigma: {pooled_stDev}\n"
                        f"Test statistics: {test_statistics}\n\n"
                        f"CV1: {thresholds[0]}\n"
                        f"CV2: {thresholds[1]}\n"
                        f"CV3: {thresholds[2]}\n")
        return ("Test not passed with confidence level of 99%\n"
                "RC determinations do not refer to the same date\n\n"
                f"Pooled mean: {pooled_mean}\n"
                f"Pooled sigma: {pooled_stDev}\n"
                f"Test statistics: {test_statistics}\n\n"
                f"CV1: {thresholds[0]}\n"
                f"CV2: {thresholds[1]}\n"
                f"CV3: {thresholds[2]}\n")
    elif 0 < confidence_level <= 100:
        if test_statistics < thresholds[0]:
            return (f"Test passed at confidence level of {confidence_level}%\n"
                    f"RC determinations may refer to the same date\n\n"
                    f"Best estimated date: {pooled_mean} +/- {pooled_stDev}\n"
                    f"Pooled mean: {pooled_mean}\n"
                    f"Pooled sigma: {pooled_stDev}\n"
                    f"Test statistics: {test_statistics}\n\n"
                    f"CV: {thresholds[0]}\n")
        return (f"Test not passed with confidence level of {confidence_level}%\n"
                "RC determinations do not refer to the same date\n\n"
                f"Pooled mean: {pooled_mean}\n"
                f"Pooled sigma: {pooled_stDev}\n"
                f"Test statistics: {test_statistics}\n\n"
                f"CV: {thresholds[0]}\n")
    else:
        raise Exception('Confidence level expressed in the wrong format')


def run(dataset_file, output_folder, confidence_level=0):
    '''reads the input csv file with RC determinations and prints
    the result of the test of Ward and Wilson'''

    # script starts here
    startTime = time.time()

    # dataset_file is the csv file containing the dataset
    if not os.path.exists(dataset_file):
        raise Exception('Unable to find dataset.csv')

    datesDict, phasesDict = read_dates(dataset_file)
    meanDict = {dateID: datesDict[dateID][0] for dateID in sorted(datesDict.keys())}
    stDevDict = {dateID: datesDict[dateID][1] for dateID in sorted(datesDict.keys())}
    
    pm_num = sum(float(meanDict[dateID]) / float(stDevDict[dateID])**2 for dateID in meanDict)
    pm_den = sum(1 / float(stDevDict[dateID])**2 for dateID in stDevDict)
    pooled_mean = pm_num / pm_den
    pooled_var = 1 / pm_den
    pooled_stDev = math.sqrt(pooled_var)

    test_statistics = sum(((float(meanDict[dateID]) - pooled_mean)**2) / float(stDevDict[dateID])**2 for dateID in meanDict)

    if confidence_level == 0:
        thresholds = list(stats.chi2.ppf([0.90, 0.95, 0.99], len(meanDict) - 1))
    elif 0 < confidence_level <= 100:
        thresholds = list(stats.chi2.ppf([float(confidence_level) / 100], len(meanDict) - 1))
    else:
        raise Exception('Confidence level expressed in the wrong format')

    std_out = generate_output(test_statistics, pooled_mean, pooled_stDev, confidence_level, thresholds)

    endTime = time.time()
    std_out += "\nScript runtime: " + str((endTime - startTime)) + " seconds"

    # saves std_out results
    save_std_out(output_folder, std_out)


def launch(**kwargs):
    current_dir = os.getcwd()
    dataset_file = current_dir + os.path.sep + "dataset.csv"
    run(dataset_file=dataset_file, output_folder=current_dir, **kwargs)


if __name__ == '__main__':
    launch()