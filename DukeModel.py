import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.integrate import odeint

T_end = 100  # In Days

# ON CAMPUS VARIABLES
Susceptible_c = np.zeros(T_end)
Susceptible_c[0] = 2000

Undetected_c = np.zeros(T_end)
Undetected_c[0] = 6

Iso_un_c = np.zeros(T_end)  # false pos
Iso_in_c = np.zeros(T_end)  # true pos
Sympt_c = np.zeros(T_end)  # Symptomatic
Vaccinated_c = np.zeros(T_end)
Recovered_c = np.zeros(T_end)
Deaths_c = np.zeros(T_end)

# OFF CAMPUS VARIABLES
Susceptible_o = np.zeros(T_end)
Susceptible_o[0] = 2000

Undetected_o = np.zeros(T_end)
Undetected_o[0] = 5

Iso_un_o = np.zeros(T_end)  # false pos
Iso_in_o = np.zeros(T_end)  # true pos
Sympt_o = np.zeros(T_end)  # Symptomatic
Recovered_o = np.zeros(T_end)
Vaccinated_o = np.zeros(T_end)
Deaths_o = np.zeros(T_end)

totSusceptible = np.zeros(T_end)
totUndetected = np.zeros(T_end)

death = 0.00004
recovery_rate = (1 / 14)
symptom_onset = 0.06122
mu = (1 / 14)  # false positives returned
sensitivity = .8
specificity = .98
vaccineEfficacy = .9  #
vaccineDate = 0

# SWEEP VARIABLES
R_stu_range = np.array([1, 1.5, 2, 3])
R_c = .5

screening_range = np.array([1, 2, 3]) / 7  # days per week

X_range = np.array([0, .0035, .007]) / 7  # infections per week
Y_range = np.array([0, .0105, .021]) / 7

VaccineDist = np.array([50,100,150, 200]) / 7   # Daily vaccine distribution

#dataFile = open("CompiledData.csv", "w")
#dataFile.write("Total, Recovered, On Campus, Off Campus, R_stu, Screening, X, Y, Vaccinations, Max Infected Time \n")

def InitializeVars():
    # ON CAMPUS VARIABLES
    Susceptible_c = np.zeros(T_end)
    Susceptible_c[0] = 2000

    Undetected_c = np.zeros(T_end)
    Undetected_c[0] = 6

    Iso_un_c = np.zeros(T_end)  # false pos
    Iso_in_c = np.zeros(T_end)  # true pos
    Sympt_c = np.zeros(T_end)  # Symptomatic
    Vaccinated_c = np.zeros(T_end)
    Recovered_c = np.zeros(T_end)
    Deaths_c = np.zeros(T_end)

    # OFF CAMPUS VARIABLES
    Susceptible_o = np.zeros(T_end)
    Susceptible_o[0] = 2000

    Undetected_o = np.zeros(T_end)
    Undetected_o[0] = 5

    Iso_un_o = np.zeros(T_end)  # false pos
    Iso_in_o = np.zeros(T_end)  # true pos
    Sympt_o = np.zeros(T_end)  # Symptomatic
    Recovered_o = np.zeros(T_end)
    Vaccinated_o = np.zeros(T_end)
    Deaths_o = np.zeros(T_end)

    totSusceptible = np.zeros(T_end)
    totUndetected = np.zeros(T_end)
    print("cleared")


def plot(Susceptible, Undetected, Symptomatic, Recovered, Dead, Fp, Tp, t, name, dir, sweptVar, maxInfected):
    fig = plt.figure(num=1, clear=True)
    ax = fig.add_subplot(1, 1, 1)
    # Plot using red circles
    # ax.plot(t, G, 'b-', label='Oral OP Concentration (μg/L)', markevery=10)

    # ax.plot(t, U, 'g-', label='Uninfected')
    """
    ax.plot(t, A, 'b-', label='Undetected (Asymptomatic)')
    ax.plot(t, S, 'r-', label='Isolated (Symptomatic)')
    #ax.plot(t, R, 'm-', label='Recovered')
    #ax.plot(t, Fp, 'c-', label='Isolated (Uninfected)')
    ax.plot(t, Tp, 'y-', label='Isolated (Asymptomatic)')
    ax.plot(t, D, 'k-', label='Dead')
    """

    totalInfectedIsolated = np.array([Symptomatic, Tp]).sum(axis=0)
    totalVaccinated = np.array([Vaccinated_o, Vaccinated_c]).sum(axis=0)
    totalSusceptible = np.array([Susceptible_c, Susceptible_o]).sum(axis=0)
    ax.plot(t, Undetected, 'g-', label='Infected (Undetected)')
    ax.plot(t, totalInfectedIsolated, 'r-', label='Infected (Isolated)')
    if maxInfected:
        plt.axvline(x=maxInfected, color='r', ls="--",  label="Max Infected")
    """ax.plot(t, totalVaccinated, 'b-', label="Vaccinated")
    ax.plot(t, totalSusceptible, 'k-', label="Susceptible")"""

    # Set labels and turn grid on
    ax.set(xlabel='Time, Days', ylabel=r'Population')
    ax.grid(True)
    ax.legend(loc='best')
    # Use space most effectively
    fig.tight_layout()
    fig.savefig("{}/{}_{}.png".format(dir, name.replace(' ', '_'), sweptVar))
    fig.show()


def OnCampus(t, R_stu, screening, X, vaccineDist):
    infectedFrac = (
            totUndetected[t] / (totSusceptible[t] + totUndetected[t]))  # Fraction of non-isolated students infected

    infectedFrac_c = Undetected_c[t] / (Susceptible_c[t] + Undetected_c[t]) # Fraction of on-campus non-isolated students infected

    Beta_stu = (recovery_rate + symptom_onset) * R_stu  # Each student to each student
    Beta_c = (recovery_rate + symptom_onset) * R_c  # Between on campus students

    if t % 7 == 0 and Susceptible_c[t] >= X:
        x = X
        # print("New Infections On Campus: {:.3}".format(Iso_in_c[t]+Sympt_c[t]))
    else:
        x = 0

    # print(infectedFrac, infectedFrac_c)

    Susceptible_c[t + 1] = Susceptible_c[t] * (1 - Beta_stu * infectedFrac - Beta_c * infectedFrac_c) \
                           - Susceptible_c[t - 1] * screening * (1 - specificity) + mu * Iso_un_c[t] - x*Susceptible_c[t] \
                            - vaccineDist * vaccineEfficacy * (t>vaccineDate)

    #print(totSusceptible[t])
    Undetected_c[t + 1] = Undetected_c[t] * (1 - symptom_onset - recovery_rate) \
                          + Susceptible_c[t] * (Beta_stu * infectedFrac + Beta_c * infectedFrac_c)\
                          - Undetected_c[t - 1] * screening * sensitivity + x*Susceptible_c[t]

    Iso_un_c[t + 1] = Iso_un_c[t] * (1 - mu) + Susceptible_c[t - 1] * screening * (1 - specificity)

    Iso_in_c[t + 1] = Iso_in_c[t] * (1 - symptom_onset - recovery_rate) + Undetected_c[t - 1] * screening * sensitivity

    Sympt_c[t + 1] = Sympt_c[t] * (1 - recovery_rate - death) + symptom_onset * (Iso_in_c[t] + Undetected_c[t])

    Vaccinated_c[t + 1] = Vaccinated_c[t] + vaccineDist * vaccineEfficacy

    Recovered_c[t + 1] = Recovered_c[t] + recovery_rate * (Iso_in_c[t] + Undetected_c[t] + Sympt_c[t])

    Deaths_c[t + 1] = Deaths_c[t] + death * Sympt_c[t]


    if Susceptible_c[t+1] <= 0:
        Susceptible_c[t] = 0

    # if t % 21 == 0:
    # print("True Pos:{}, Asympt: {}, Sympt: {}".format(Iso_in_c[t], Undetected_c[t], Sympt_c[t]))


def OffCampus(t, R_stu, screening, Y, vaccineDist):
    infectedFrac = (
            totUndetected[t] / (totSusceptible[t] + totUndetected[t]))  # Fraction of non-isolated students infected

    Beta_stu = (recovery_rate + symptom_onset) * R_stu  # Each student to each student

    if t % 7 == 0 and Susceptible_o[t] >= Y:
        # print("New Infections Off Campus: {}".format(Iso_in_o[t]+Sympt_o[t]))
        y = Y
    else:
        y = 0

    Susceptible_o[t + 1] = Susceptible_o[t] * (
            1 - Beta_stu * infectedFrac) - Susceptible_o[t - 1] * screening * (1 - specificity) + \
                           mu * Iso_un_o[t] - y*Susceptible_o[t] - vaccineDist *vaccineEfficacy * (t>vaccineDate)

    Undetected_o[t + 1] = Undetected_o[t] * (1 - symptom_onset - recovery_rate) + \
                          Beta_stu * Susceptible_o[t] * infectedFrac \
                          - Undetected_o[t - 1] * screening * sensitivity + y*Susceptible_o[t]

    Iso_un_o[t + 1] = Iso_un_o[t] * (1 - mu) + Susceptible_o[t - 1] * screening * (1 - specificity)

    Iso_in_o[t + 1] = Iso_in_o[t] * (1 - symptom_onset - recovery_rate) + Undetected_o[t - 1] * screening * sensitivity

    Sympt_o[t + 1] = Sympt_o[t] * (1 - recovery_rate - death) + symptom_onset * (Iso_in_o[t] + Undetected_o[t])

    Vaccinated_o[t + 1] = Vaccinated_o[t] + vaccineEfficacy * vaccineDist

    Recovered_o[t + 1] = Recovered_o[t] + recovery_rate * (Iso_in_o[t] + Undetected_o[t] + Sympt_o[t])

    Deaths_o[t + 1] = Deaths_o[t] + death * Sympt_o[t]

    if Susceptible_o[t+1] <= 0:
        Susceptible_o[t] = 0
    if (Susceptible_c[t] * (Beta_stu * infectedFrac)) <= .074:
        print("No new growth when Vaccinated: {}\n Recovered: {}"
              .format(Vaccinated_o[t], Recovered_o[t] ))
    # if t % 21 == 0:
    # print("True Pos:{}, Asympt: {}, Sympt: {}".format(Iso_in_o[t], Undetected_o[t], Sympt_o[t]))


def Model (R_stu, screening, X, Y, vaccineDist, dir, sweptVar):

    time = range(0, T_end)

    for t in time[0:T_end - 1]:

        totSusceptible[t] = Susceptible_c[t] + Susceptible_o[t]
        totUndetected[t] = Undetected_c[t] + Undetected_o[t]
        OnCampus(t, R_stu, screening, X, vaccineDist)
        OffCampus(t, R_stu, screening, Y, vaccineDist)

    maxInfected = np.argmax(np.array([Undetected_c, Undetected_o,
                                   Iso_in_o, Iso_in_c, Sympt_o,Sympt_c]).sum(axis=0))
    print("Max Infected at {}".format(maxInfected))

    print("Total Recovered {} On Campus: {}, Off Campus {}\n R:{}, Screening:{}, X:{}, Y:{},Vaccine : {} per week"
          .format(Recovered_c[99] + Recovered_o[99], Recovered_c[99],
                                         Recovered_o[99], R_stu, screening, X, Y, vaccineDist*7))
    newData = ([Recovered_c[99] + Recovered_o[99], Recovered_c[99], Recovered_o[99], R_stu, screening*7, X, Y,
                vaccineDist * vaccineEfficacy*7, maxInfected])

    newData = str(newData).replace("[", "").replace("]", "")
    #dataFile.write(newData+"\n")

    campusData = (Susceptible_c, Undetected_c, Sympt_c, Recovered_c, Deaths_c, Iso_un_c, Iso_in_c)
    offCampusData = (Susceptible_o, Undetected_o, Sympt_o, Recovered_o, Deaths_o, Iso_un_o, Iso_in_o)

    plot(Susceptible_c, Undetected_c, Sympt_c, Recovered_c, Deaths_c, Iso_un_c, Iso_in_c, time, "On Campus",
         dir, sweptVar, 0)
    plot(Susceptible_o, Undetected_o, Sympt_o, Recovered_o, Deaths_o, Iso_un_o, Iso_in_o, time, "Off Campus",
         dir, sweptVar, 0)
    plot(np.add(Susceptible_c, Susceptible_o),
         np.add(Undetected_c, Undetected_o),
         np.add(Sympt_c, Sympt_o),
         np.add(Recovered_c, Recovered_o),
         np.add(Deaths_c, Deaths_o),
         np.add(Iso_un_c, Iso_un_o),
         np.add(Iso_in_c, Iso_in_o),
         time, "Overall Data", dir, sweptVar, maxInfected)
    InitializeVars()


swept = int(input("Select Sweep Variable \n 1) Inter-Student R \n 2) Screening Frequency \n 3) Exogenous Shocks \n "
                  "4) Vaccine Availibility\n 5)All of the Above\n"))


def Sweep(sweepVar):
    if sweepVar == 1:
        for r in R_stu_range:
            Model(r, screening_range[1], X_range[1], Y_range[1], 0, "R_Stu", "r_{}".format(r))

    elif sweepVar == 2:
        for screen in screening_range:
            Model(R_stu_range[1], screen, X_range[1], Y_range[1], 0, "Screening", "Screening_{}".format(screen * 7))
    elif sweepVar == 3:
        for shock in range(0, 3):
            Model(R_stu_range[1], screening_range[1], X_range[shock], Y_range[shock], 0, "Exogenous",
                  "ShockLevel_{}".format(shock))
    elif sweepVar == 4:
        for vaccineDist in VaccineDist:
            print(vaccineDist)
            Model(R_stu_range[1], screening_range[1], X_range[1], Y_range[1], vaccineDist, "Vaccine",
                  "Vaccine_{}".format(vaccineDist * 7))


if swept == 5:
    for sweepVar in range(1, 5):
        Sweep(sweepVar)
else:
    Sweep(swept)

#dataFile.close()
