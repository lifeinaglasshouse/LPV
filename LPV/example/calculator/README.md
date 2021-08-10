# CalculatorPy
## Calculator written in Python using LPV

### DEMO:
```
>>> 1+1
2
>>> 2*2
4
>>> (2*)2
Parser::Error Occurred:
  ───┬───────
   1 │ (2*)2
     │    └─┤col:4│
SyntaxError: Unexpected ')', expected valid expression
>>>
```

### Using it on your Python Application:
Install LPV. Download calc.py
```py
import calc

print(calc.calculate("1+(2*2)")) # 5
print(calc.calculate("(((((((((2)))))))))")) # 2
print(calc.calculate("2)")) # 2?
print(calc.calculate("*(")) # LPV_Exception
print(calc.calculate(<Possible input that can break the calc>)) # Calc Crash
```