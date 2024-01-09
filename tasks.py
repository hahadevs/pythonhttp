from math import pi

def fibonacci(n:int=None):
    """1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144...."""
    if n is None: n = 5
    elif n == 0 : return []
    elif n == 1 : return [1]
    elif n == 2 : return [1,2]
    i = 2
    series = [1,2]
    while i < n:
        series.append(series[-1] + series[-2])
        i += 1
    return series
def area_of_circle(radius:int=None):
    if radius:
        return pi*radius*radius
    return "Please Pass radius of circle as a function argument ."

def celcius_to_fh():
    """Convert the celcius to Fahrenheit"""
    cel = int(input("Enter the temperature in Celcius : "))
    print("Temperature in Fahrenheit is : ",((cel*9)/5)+32)
if __name__ == '__main__':
    # print(area_of_circle())
    # print(fibonacci(3))
    celcius_to_fh()