# User input of the location coordinates
print("Enter your location in British National Grid Coordinate System:")
user_easting = float(input("Easting: "))
user_northing = float(input("Northing: "))
easting_limit_left = 430000
northing_limit_left = 80000
easting_limit_right = 465000
northing_limit_right = 95000
if not (easting_limit_left <= user_easting <= easting_limit_right and northing_limit_left <= user_northing <= northing_limit_right):
    print("Sorry, Your Location is NOT within this corresponding boundary limits")
