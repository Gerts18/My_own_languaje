grammar Language;

program
    : (instruccion)*
    ;

instruccion
    : declaracion SEMI
    | asignacion SEMI
    | expr SEMI
    | if_estructura
    | print_instr
	| for_estructura  // Cambiado a Recorre
    | bloque
    ;

declaracion
    : tipo ID ('->' expr)?   
    ;

asignacion
    : ID '->' expr
    ;

tipo
    : 'ent'
    | 'dec'
    | 'band'
    | 'cadena'
    ;

if_estructura
    : 'SoloSi' '(' condicional ')' bloque ('SoloSiTamb' '(' condicional ')' bloque)* ('SiNo' bloque)?
    ;

bloque
    : '{' instruccion* '}'
    ;

condicional
    : condicional AND condicional
    | condicional OR condicional
    | expr op=(MENORQUE|MAYORQUE|MENORIGUAL|MAYORIGUAL|IGUAL|DIFERENTE) expr
    | '(' condicional ')'
    ;

expr
    : termino (('(suma)'|'(resta)') termino)*
    ;

termino
    : factor (('(mult)'|'(div)') factor)*
    ;

factor
    : NUM
    | STRING
    | BOOLEAN
    | ID
    | '(' expr ')'
    ;

for_estructura
    : 'Recorre' '(' 
      (declaracion | asignacion | ID)? SEMI  // Inicialización (opcional, ahora acepta solo ID)
      condicional? SEMI                      // Condición (opcional)
      (asignacion | expr)?                   // Incremento (opcional)
      ')' bloque
    ;

print_instr
    : 'Imprime' '(' expr ')' ';'  // Definimos la sintaxis de print
    ;


// Tokens
NUM: [0-9]+ ('.' [0-9]+)?;  // Enteros y flotantes
STRING: '"' .*? '"';
BOOLEAN: 'true' | 'false';
SEMI: ';';
WS: [ \t\n\r\f]+ -> skip;
ID: [a-zA-Z_][a-zA-Z_0-9]*;

// Operadores
OP_ASIGN: '->';
OP_SUMA: '(suma)';
OP_RESTA: '(resta)';
OP_MULT: '(mult)';
OP_DIV: '(div)';
// Cambia los operadores de comparación a palabras clave entre corchetes
MENORQUE: '[menorQue]';
MAYORQUE: '[mayorQue]';
MENORIGUAL: '[menorIgual]';
MAYORIGUAL: '[mayorIgual]';
IGUAL: '[igual]';
DIFERENTE: '[diferente]';
AND: '[Y]';
OR: '[oTambien]';