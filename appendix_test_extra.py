"""Test evaluation of automatas."""
import unittest
from abc import ABC

from src.automaton import FiniteAutomaton
from src.utils import AutomataFormat, deterministic_automata_isomorphism, write_dot
from src.re_parser import REParser


class TestTransform2(ABC, unittest.TestCase):
    """Base class for string acceptance tests."""
    def _check_accept(self, evaluator, string, should_accept = True):
        with self.subTest(string=string):
            accepted = evaluator.accepts(string)
            self.assertEqual(accepted, should_accept)

    def test_case_extra1(self):
        """Test Case_extra 1."""
        automaton = REParser().create_automaton('a*')

        transformed = automaton.to_deterministic()
        

        expected_str = """
        Automaton:
        Symbols: a

        s3s0s2 final
        s1s0s3 final

        ini s3s0s2 -a-> s1s0s3
        s1s0s3 -a-> s1s0s3
        
        """

        expected = AutomataFormat.read(expected_str)
        
        equiv_map = deterministic_automata_isomorphism(expected, transformed)

        self.assertTrue(equiv_map is not None)
    
    def test_case_extra2(self):
        """Test Case_extra 2."""
        automaton = REParser().create_automaton('(a+b)*')

        transformed = automaton.to_deterministic()

        min = transformed.to_minimized()

        expected_transformed_str = """
        Automaton:
        Symbols: ba

        s2s6s3s0s4 final
        s2s6s0s4s5 final
        s2s6s0s4s1 final

        ini s2s6s0s4s5 -b-> s2s6s3s0s4
        s2s6s0s4s5 -a-> s2s6s0s4s1
        s2s6s3s0s4 -b-> s2s6s3s0s4
        s2s6s3s0s4 -a-> s2s6s0s4s1
        s2s6s0s4s1 -b-> s2s6s3s0s4
        s2s6s0s4s1 -a-> s2s6s0s4s1
        
        """

        expected_min_str = """
        Automaton:
        Symbols: ab

        0 final

        ini 0 -a-> 0
        0 -b-> 0
        """

        expected_transformed = AutomataFormat.read(expected_transformed_str)
        expected_min = AutomataFormat.read(expected_min_str)

        equiv_map = deterministic_automata_isomorphism(expected_transformed, transformed)
        self.assertTrue(equiv_map is not None)

        equiv_map = deterministic_automata_isomorphism(expected_min, min)
        self.assertTrue(equiv_map is not None)

    def test_case0(self):
        """Test Case 0."""
        automaton = REParser().create_automaton('(a+b)*.a')

        transformed = automaton.to_deterministic()

        expected_transformed_str = """
        Automaton:
        Symbols: ba

        s0s8s4s1s6s2s7 final
        s0s3s4s6s2s7
        s0s4s5s6s2s7

        ini s0s4s5s6s2s7 -b-> s0s3s4s6s2s7
        s0s4s5s6s2s7 -a-> s0s8s4s1s6s2s7
        s0s3s4s6s2s7 -b-> s0s3s4s6s2s7
        s0s3s4s6s2s7 -a-> s0s8s4s1s6s2s7
        s0s8s4s1s6s2s7 -b-> s0s3s4s6s2s7
        s0s8s4s1s6s2s7 -a-> s0s8s4s1s6s2s7
        """

        expected_min_str = """
        Automaton:
        Symbols: ab

        0 final
        1

        0 -a-> 0
        0 -b-> 1
        ini 1 -a-> 0
        1 -b-> 1
        """

        min = transformed.to_minimized()


        expected_transformed = AutomataFormat.read(expected_transformed_str)
        expected_min = AutomataFormat.read(expected_min_str)

        equiv_map = deterministic_automata_isomorphism(expected_transformed, transformed)
        self.assertTrue(equiv_map is not None)

        equiv_map = deterministic_automata_isomorphism(expected_min, min)
        self.assertTrue(equiv_map is not None)

        self._check_accept(min, "a", True)
        self._check_accept(min, "bbbbaba", True)
        self._check_accept(min, "abbab", False)
        self._check_accept(min, "b", False) 
   
    
    def test_case1(self):
        """Test Case 1."""
        """
        Expresión regular sobre el alfabeto {a,b,c} que representa las cadenas no
        vacías que contienen al menos una a y al menos una b
        
        RE1 = r"[abc]*a[abc]*b[abc]*|[abc]*b[abc]*a[abc]*"
        """
        automaton = REParser().create_automaton('((a+b+c)*.a.(a+b+c)*.b.(a+b+c)*)+((a+b+c)*.b.(a+b+c)*.a.(a+b+c)*)')
        
        transformed = automaton.to_deterministic()

        min = transformed.to_minimized()

        self._check_accept(min, "ab", True)
        self._check_accept(min, "aba", True)
        self._check_accept(min, "aab", True)
        self._check_accept(min, "cab", True)
        self._check_accept(min, "baa", True)
        self._check_accept(min, "aabc", True)
        self._check_accept(min, "acccbc", True)
        self._check_accept(min, "bcccbcacb", True)

        self._check_accept(min, "bcc", False)
        self._check_accept(min, "cc", False)
        self._check_accept(min, "aacc", False)
        self._check_accept(min, "aaa", False)
        self._check_accept(min, "b", False)
        self._check_accept(min, "bcbcbcbcbb", False)
    
    def test_case2(self):
        """Test Case 2."""
        """
        Expresión regular que representa un número arbitrario, con o sin signo y
        con o sin parte decimal.

        RE2 = r"[\-]?([1-9][0-9]*|[0]?)\.[0-9]*|[\-]?([1-9][0-9]*|[0]?)"

        Nota: para evitar conflictos con símbolos funcionales de la expresión regular,
        hemos sustituido el símbolo "." por la coma "," para representar la frontera
        entre la parte entera y la parte decimal del número.
        
        """
        automaton = REParser().create_automaton('((-+λ).(((1+2+3+4+5+6+7+8+9).(0+1+2+3+4+5+6+7+8+9+0)*)+λ).,.((0+1+2+3+4+5+6+7+8+9+0).(0+1+2+3+4+5+6+7+8+9+0)*))+((-+λ).((1+2+3+4+5+6+7+8+9).(0+1+2+3+4+5+6+7+8+9+0)*).(,+λ))+(0.((,.(0+1+2+3+4+5+6+7+8+9+0)*)+λ))+(-.0.,.((0+1+2+3+4+5+6+7+8+9+0).(0+1+2+3+4+5+6+7+8+9+0)*))')
       
        transformed = automaton.to_deterministic()

        min = transformed.to_minimized()


        self._check_accept(min, "15", True)
        self._check_accept(min, "-18", True)
        self._check_accept(min, "14,33", True)
        self._check_accept(min, "-147,33", True)
        self._check_accept(min, "-147,", True)
        self._check_accept(min, "-,33", True)
        self._check_accept(min, ",33", True)
        self._check_accept(min, "0,98", True)
        self._check_accept(min, "-0,7", True)

        self._check_accept(min, ",", False)
        self._check_accept(min, "-0", False)
        self._check_accept(min, "14,4,5", False)
        self._check_accept(min, "014,4", False)
        self._check_accept(min, "-04,5", False)
        self._check_accept(min, "-1,2,", False)
        self._check_accept(min, "-1-2", False)
        self._check_accept(min, ".4-2", False)
        self._check_accept(min, "2,,5", False)
        
    
    def test_case3(self):
        """Test Case 3."""
        """
        Expresión regular que representa direcciones web de una de las dos
        formas siguientes: www.uam.es/extensión o moodle.uam.es/extensión. En ambos
        casos la extensión es una cadena formada por letras minúsculas y el símbolo /, que
        puede estar vacía. En ningún caso podrán aparecer dos símbolos / seguidos.

        RE3 = r"(www.uam.es|moodle.uam.es)/([a-z]+/)*[a-z]*"
        """
        automaton = REParser().create_automaton('((w.w.w.,.u.a.m.,.e.s)+(m.o.o.d.l.e.,.u.a.m.,.e.s))./.(((a+b+c+d+e+f+g+h+i+j+k+l+m+n+ñ+o+p+q+r+s+t+u+v+w+x+y+z).(a+b+c+d+e+f+g+h+i+j+k+l+m+n+ñ+o+p+q+r+s+t+u+v+w+x+y+z)*)./)*.(a+b+c+d+e+f+g+h+i+j+k+l+m+n+ñ+o+p+q+r+s+t+u+v+w+x+y+z)*')
        transformed = automaton.to_deterministic()

        min = transformed.to_minimized()

        self._check_accept(min, "moodle,uam,es/", True)
        self._check_accept(min, "moodle,uam,es/luis/hebrero", True)
        self._check_accept(min, "moodle,uam,es/k/e/aa", True)
        self._check_accept(min, "moodle,uam,es/", True)
        self._check_accept(min, "www,uam,es/patata", True)
        self._check_accept(min, "www,uam,es/", True)
        self._check_accept(min, "moodle,uam,es/t/", True)

        self._check_accept(min, "tomate", False)
        self._check_accept(min, "www,uam,es", False)
        self._check_accept(min, "www,uam,es//t", False)
        self._check_accept(min, "www,uam,es/t//o", False)
        self._check_accept(min, "www,uam,es/Yo", False)
        self._check_accept(min, "www,uam,es/u7/i", False)
        self._check_accept(min, "www,uam,es/?/i", False)
        self._check_accept(min, "owww,uam,es/o", False)
        self._check_accept(min, "tomate pera 1.67€/kg", False)



    def test_case4(self):
        """Test Case 4."""
        """
        expresión regular que representa expresiones aritméticas con números
        enteros positivos (se excluye el 0) y los símbolos +, -, * y /
        
        RE4 = r"[1-9][0-9]*([+\-*/][1-9][0-9]*)*"

        Nota: para evitar conflictos con símbolos funcionales de la expresión regular,
        se ha sustituido el símbolo de la suma (+) por el símbolo "#" y el de la multiplicación
        (*) por "x".
        """

        automaton = REParser().create_automaton('(1+2+3+4+5+6+7+8+9).(0+1+2+3+4+5+6+7+8+9)*.((#+-+x+/).(1+2+3+4+5+6+7+8+9).(0+1+2+3+4+5+6+7+8+9)*)*')
        transformed = automaton.to_deterministic()

        min = transformed.to_minimized()

        self._check_accept(min, "10#2", True)
        self._check_accept(min, "24#1-6x7/8", True)
        self._check_accept(min, "150", True)
        self._check_accept(min, "15/5", True)
        self._check_accept(min, "22#3/1#3#3", True)
        
        self._check_accept(min, "21xx4", False)
        self._check_accept(min, "3#", False)
        self._check_accept(min, "-4", False)
        self._check_accept(min, "8#-3", False)
        self._check_accept(min, "0", False)
        self._check_accept(min, "2#0-6", False)
        self._check_accept(min, "21#8--3/6", False)
        self._check_accept(min, "21#8-e#3/6", False)
        self._check_accept(min, "21#8-e3/6", False)
        self._check_accept(min, "caceres", False)

    def test_case4(self):
        """Test Case 5."""
        """
        Expresión regular que represente expresiones aritméticas con números enteros 
        positivos (se excluye el 0) y los símbolos +, -, * y /, en las que se permite el
        uso de paréntesis sin anidamiento
        
        RE5 = r"(([1-9]+[0-9]*)|(\(([1-9]+[0-9]*)([+\-*/]([1-9]+[0-9]*))*\)))([+\-*/](([1-9]+[0-9]*)|(\(([1-9]+[0-9]*)([+\-*/]([1-9]+[0-9]*))*\))))*"
        
        Nota: para evitar conflictos con símbolos funcionales de la expresión regular,
        se ha sustituido el símbolo de la suma (+) por el símbolo #, el de la multiplicación
        (*) por x, y los paréntesis ("()") por corchetes ("[]")
        """

        automaton = REParser().create_automaton('(((1+2+3+4+5+6+7+8+9).(0+1+2+3+4+5+6+7+8+9)*)+([.((1+2+3+4+5+6+7+8+9).(0+1+2+3+4+5+6+7+8+9)*).((#+-+x+/).((1+2+3+4+5+6+7+8+9).(0+1+2+3+4+5+6+7+8+9)*))*.])).((#+-+x+/).(((1+2+3+4+5+6+7+8+9).(0+1+2+3+4+5+6+7+8+9)*)+([.((1+2+3+4+5+6+7+8+9).(0+1+2+3+4+5+6+7+8+9)*).((#+-+x+/).((1+2+3+4+5+6+7+8+9).(0+1+2+3+4+5+6+7+8+9)*))*.])))*')
        transformed = automaton.to_deterministic()

        min = transformed.to_minimized()

        self._check_accept(min, "[3#4]x5/2-[4]x3", True)
        self._check_accept(min, "[4]", True)
        self._check_accept(min, "6", True)
        self._check_accept(min, "6-1x7", True)
        self._check_accept(min, "8x[7/4]", True)
        self._check_accept(min, "[7#2-1]x[7]", True)
        self._check_accept(min, "[7#2-17]", True)
        self._check_accept(min, "2-[4]", True)
        self._check_accept(min, "2-[4]#[8]/[43x17-333]", True)

        self._check_accept(min, "2#7-[2#0]", False)
        self._check_accept(min, "0", False)
        self._check_accept(min, "2[4x6]", False)
        self._check_accept(min, "[3#5-2x]3", False)
        self._check_accept(min, "45x121-[43#4", False)
        self._check_accept(min, "45xx121", False)


if __name__ == '__main__':
    unittest.main()
