# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 10:24:05 2020

@author: Florian Jehn

This program calculates how much different countries are affected, when
other countries reduce the amount of food they export. 
"""
import pandas as pd
import os


# Countries that reduce their food amount and to what level they change their
# export. E.g. Iraq:0.7 refers to Iraq reducing its exports to 70 % of  their
# usual levels
reducers = {"Russian Federation": 0.75, "Kazakhstan":0.0, "China, mainland":0.8,
            "Italy": 0.5, "Iran (Islamic Republic of)": 0.5}

# Get the trade data
trade = pd.read_csv("trade_by_country_2017.csv", sep=";")
trade = trade.loc[trade["Y2017"] > 0,:]
imports = trade.loc[trade["Element"] == "Import Quantity",:]
exports = trade.loc[trade["Element"] == "Export Quantity",:]

# Test if the names are written correctly:
for country in reducers.keys():
    if country not in list(trade["Reporter Countries"].unique()):
        raise NameError(country + " not in dataset. Please make sure it is spelled correctly. See code below to find all possible name")

# Only consider the countries that reduce
export_reducers = exports.loc[exports["Reporter Countries"].isin(list(reducers.keys())),:]

# Calculate the exports of those countries before they reduce
original_exports = export_reducers.groupby("Partner Countries").sum()

# Reduce export by reduction factor
for country in reducers.keys():
    export_reducers.loc[export_reducers["Reporter Countries"] == country,"Y2017"] *= export_reducers["Reporter Countries"].map(reducers)

# Calculate the sum of the remaining exports by country
remaining_exports = round(export_reducers.groupby("Partner Countries").sum(),0)

# Calculate Reduction
export_reduction = round(original_exports - remaining_exports,0)

# Calculate how much imports the countires hit by the reduction receive overall (before reduction)
original_imports = imports.loc[imports["Reporter Countries"].isin(remaining_exports.index),:].groupby("Reporter Countries").sum()

# Combine in one df
changes = pd.concat([original_imports, export_reduction], axis = 1)
changes.columns = ["Imports before reduction [t]", "Total import reduction [t]"]

# Calculate changes
changes["Imports after reduction [t]"] = changes["Imports before reduction [t]"] - changes["Total import reduction [t]"]
changes["Remaining Imports [%]"] = round((changes["Imports after reduction [t]"] / changes["Imports before reduction [t]"]) * 100,0)
changes.dropna(inplace=True)
changes.to_csv("import_export_changes.csv", sep=";")




