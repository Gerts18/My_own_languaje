package milenguaje;

import java.util.HashMap;
import java.util.Map;

import org.antlr.v4.runtime.tree.TerminalNode;


public class LanguageCustomVisitor extends LanguageBaseVisitor<Object> {

    private final Map<String, Object> memory = new HashMap<>();
    private int scopeLevel = 0;

    @Override
    public Object visitProgram(LanguageParser.ProgramContext ctx) {
        ctx.instruccion().forEach(this::visit);
        return null;
    }

    @Override
    public Object visitDeclaracion(LanguageParser.DeclaracionContext ctx) {
        String type = ctx.tipo().getText();
        String varName = ctx.ID().getText();
        Object value = ctx.expr() != null ? visit(ctx.expr()) : null;

        if (memory.containsKey(varName)) {
            throw new RuntimeException("Variable ya declarada: " + varName);
        }

        if (value == null) {
            throw new RuntimeException("Variable no inicializada: " + varName);
        }

        switch (type) {
            case "ent":
                if (value instanceof Double) {
                    value = ((Double) value).intValue();
                }
                memory.put(varName, (Integer) value);
                break;
                
            case "dec":
                if (value instanceof Integer) {
                    value = ((Integer) value).doubleValue();
                }
                memory.put(varName, (Double) value);
                break;
                
            case "band":
                Boolean boolValue = (value instanceof Integer) ? 
                    ((Integer) value != 0) : (Boolean) value;
                memory.put(varName, boolValue);
                break;
                
            case "cadena":
                memory.put(varName, value.toString());
                break;
                
            default:
                throw new RuntimeException("Tipo desconocido: " + type);
        }
        return null;
    }

    @Override
    public Object visitFactor(LanguageParser.FactorContext ctx) {
        if (ctx.NUM() != null) {
            String num = ctx.NUM().getText();
            return num.contains(".") ? Double.valueOf(num) : Integer.valueOf(num);
        }
        if (ctx.STRING() != null) {
            return ctx.STRING().getText().replace("\"", "");
        }
        if (ctx.BOOLEAN() != null) {
            return ctx.BOOLEAN().getText().equals("true");
        }
        if (ctx.ID() != null) {
            String varName = ctx.ID().getText();
            return memory.getOrDefault(varName, 0);
        }
        return visit(ctx.expr());
    }

    @Override
    public Integer visitFor_estructura(LanguageParser.For_estructuraContext ctx) {
        Map<String, Object> prevMemory = new HashMap<>(memory);

        boolean declaredInFor = false;
        String declaredVarName = null;

        // Inicialización
        if (ctx.declaracion() != null) {
            visit(ctx.declaracion());
            declaredInFor = true;
            declaredVarName = ctx.declaracion().ID().getText();
        } else if (ctx.asignacion() != null && !ctx.asignacion().isEmpty()) {
            visit(ctx.asignacion(0));
        } else if (ctx.ID() != null) {
            // Solo ID en la inicialización: asegurarse que existe la variable
            String varName = ctx.ID().getText();
            if (!memory.containsKey(varName)) {
                throw new RuntimeException("Variable no declarada: " + varName);
            }
            // No se hace nada, solo se usará el valor actual de la variable
            declaredVarName = varName;
        }

        while (true) {
            // Condición
            if (ctx.condicional() != null) {
                int condition = (Integer) visit(ctx.condicional());
                if (condition == 0) break;
            }

            visit(ctx.bloque());

            // Incremento (puede ser asignación o expresión)
            if (ctx.asignacion() != null && !ctx.asignacion().isEmpty()) {
                // Si hay dos asignaciones, la segunda es el incremento
                if (ctx.asignacion().size() == 2) {
                    visit(ctx.asignacion(1));
                } else if (ctx.asignacion().size() == 1) {
                    visit(ctx.asignacion(0));
                }
            } else if (ctx.expr() != null) {
                visit(ctx.expr());
            }
        }

        // Si la variable fue declarada en el for, eliminarla al salir
        if (declaredInFor && declaredVarName != null) {
            memory.remove(declaredVarName);
            // Restaurar cualquier otra variable que haya sido modificada
            for (String key : prevMemory.keySet()) {
                if (!key.equals(declaredVarName)) {
                    memory.put(key, prevMemory.get(key));
                }
            }
        }
        // Si solo era un ID, no eliminar la variable, solo mantener los cambios
        return 0;
    }

    @Override
    public Integer visitIf_estructura(LanguageParser.If_estructuraContext ctx) {
        if (evaluateCondition(ctx.condicional(0))) {
            visit(ctx.bloque(0));
            return 1;
        }
        
        for (int i = 1; i < ctx.condicional().size(); i++) {
            if (evaluateCondition(ctx.condicional(i))) {
                visit(ctx.bloque(i));
                return 1;
            }
        }
        
        if (ctx.bloque().size() > ctx.condicional().size()) {
            visit(ctx.bloque(ctx.bloque().size() - 1));
        }
        
        return 0;
    }

    private boolean evaluateCondition(LanguageParser.CondicionalContext cond) {
        boolean result = (Integer) visit(cond) != 0;
        return result;
    }

    @Override
    public Object visitExpr(LanguageParser.ExprContext ctx) {
        Object result = visit(ctx.termino(0));

        for (int i = 1; i < ctx.termino().size(); i++) {
            Object term = visit(ctx.termino(i));
            int opType = ((TerminalNode) ctx.getChild(2 * i - 1)).getSymbol().getType();
            
            result = operate(result, term, 
                opType == LanguageLexer.OP_SUMA ? "+" : "-");
        }
        return result;
    }

    @Override
    public Object visitTermino(LanguageParser.TerminoContext ctx) {
        Object result = visit(ctx.factor(0));

        for (int i = 1; i < ctx.factor().size(); i++) {
            Object factor = visit(ctx.factor(i));
            int opType = ((TerminalNode) ctx.getChild(2 * i - 1)).getSymbol().getType();
            
            if (opType == LanguageLexer.OP_DIV && convertToDouble(factor) == 0.0) {
                throw new ArithmeticException("División por cero");
            }
            
            result = operate(result, factor, 
                opType == LanguageLexer.OP_MULT ? "*" : "/");
        }
        return result;
    }

    private Object operate(Object left, Object right, String op) {
        // Concatenación de cadenas si alguno es String y el operador es suma
        if (op.equals("+") && (left instanceof String || right instanceof String)) {
            return String.valueOf(left) + String.valueOf(right);
        }
        double l = convertToDouble(left);
        double r = convertToDouble(right);

        switch (op) {
            case "+": return l + r;
            case "-": return l - r;
            case "*": return l * r;
            case "/": return l / r;
            default: throw new RuntimeException("Operador inválido: " + op);
        }
    }

    private double convertToDouble(Object value) {
        if (value instanceof Integer) return ((Integer) value).doubleValue();
        if (value instanceof Double) return (Double) value;
        // Si es String y se espera número, lanzar excepción clara
        throw new RuntimeException("Valor no numérico: " + value);
    }

    @Override
    public Object visitPrint_instr(LanguageParser.Print_instrContext ctx) {
        Object value = visit(ctx.expr());
        System.out.println(value);
        return null;
    }

    @Override
    public Object visitAsignacion(LanguageParser.AsignacionContext ctx) {
        String varName = ctx.ID().getText();
        Object value = visit(ctx.expr());
        Object targetType = memory.get(varName);

        if (targetType == null) {
            throw new RuntimeException("Variable no declarada: " + varName);
        }

        // Permitir asignación entre Integer y Double según el tipo destino
        if (targetType instanceof Double) {
            if (value instanceof Integer) {
                value = ((Integer) value).doubleValue();
            } else if (!(value instanceof Double)) {
                throw new RuntimeException("Tipo incompatible para: " + varName);
            }
        } else if (targetType instanceof Integer) {
            if (value instanceof Double) {
                value = ((Double) value).intValue();
            } else if (!(value instanceof Integer)) {
                throw new RuntimeException("Tipo incompatible para: " + varName);
            }
        } else if (!targetType.getClass().equals(value.getClass())) {
            throw new RuntimeException("Tipo incompatible para: " + varName);
        }

        memory.put(varName, value);
        return null;
    }

    @Override
    public Object visitCondicional(LanguageParser.CondicionalContext ctx) {
        // Recursividad para AND
        if (ctx.AND() != null) {
            int left = (Integer) visit(ctx.condicional(0));
            int right = (Integer) visit(ctx.condicional(1));
            return (booleanToInt(left) && booleanToInt(right)) ? 1 : 0;
        }
        // Recursividad para OR
        if (ctx.OR() != null) {
            int left = (Integer) visit(ctx.condicional(0));
            int right = (Integer) visit(ctx.condicional(1));
            return (booleanToInt(left) || booleanToInt(right)) ? 1 : 0;
        }
        // Paréntesis
        if (ctx.getChildCount() == 3 && "(".equals(ctx.getChild(0).getText())) {
            return visit(ctx.condicional(0));
        }
        // Comparaciones binarias
        if (ctx.op != null) {
            Object left = visit(ctx.expr(0));
            Object right = visit(ctx.expr(1));
            switch (ctx.op.getType()) {
                case LanguageLexer.MENORQUE: return convertToDouble(left) < convertToDouble(right) ? 1 : 0;
                case LanguageLexer.MAYORQUE: return convertToDouble(left) > convertToDouble(right) ? 1 : 0;
                case LanguageLexer.MENORIGUAL: return convertToDouble(left) <= convertToDouble(right) ? 1 : 0;
                case LanguageLexer.MAYORIGUAL: return convertToDouble(left) >= convertToDouble(right) ? 1 : 0;
                case LanguageLexer.IGUAL: return left.equals(right) ? 1 : 0;
                case LanguageLexer.DIFERENTE: return !left.equals(right) ? 1 : 0;
                default: throw new RuntimeException("Operador desconocido");
            }
        }
        throw new RuntimeException("Condicional mal formada");
    }

    private boolean booleanToInt(Object value) {
        if (value instanceof Boolean) return (Boolean) value;
        if (value instanceof Integer) return (Integer) value != 0;
        throw new RuntimeException("Valor no booleano");
    }

    @Override
    public Object visitBloque(LanguageParser.BloqueContext ctx) {
        Map<String, Object> previousState = new HashMap<>(memory);
        try {
            scopeLevel++;
            ctx.instruccion().forEach(this::visit);
        } finally {
            memory.clear();
            memory.putAll(previousState);
            scopeLevel--;
        }
        return null;
    }
}