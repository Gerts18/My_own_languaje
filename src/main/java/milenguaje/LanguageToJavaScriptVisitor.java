package milenguaje;

public class LanguageToJavaScriptVisitor extends LanguageBaseVisitor<String> {

    @Override
    public String visitProgram(LanguageParser.ProgramContext ctx) {
        StringBuilder sb = new StringBuilder();
        for (LanguageParser.InstruccionContext var : ctx.instruccion()) {
            String code = visit(var);
            if (code != null) sb.append(code);
        }
        return sb.toString();
    }

    @Override
    public String visitInstruccion(LanguageParser.InstruccionContext ctx) {
        if (ctx.declaracion() != null) {
            return visit(ctx.declaracion());
        }
        if (ctx.asignacion() != null) {
            return visit(ctx.asignacion());
        }
        if (ctx.expr() != null) {
            return visit(ctx.expr()) + ";\n";
        }
        if (ctx.if_estructura() != null) {
            return visit(ctx.if_estructura());
        }
        if (ctx.print_instr() != null) {
            return visit(ctx.print_instr());
        }
        if (ctx.for_estructura() != null) {
            return visit(ctx.for_estructura());
        }
        if (ctx.bloque() != null) {
            return visit(ctx.bloque());
        }
        return "";
    }

    @Override
    public String visitDeclaracion(LanguageParser.DeclaracionContext ctx) {
        String id = ctx.ID().getText();
        String jsTipo = "var";
        String value = ctx.expr() != null ? visit(ctx.expr()) : null;
        if (value == null) {
            // Solo declaración sin inicialización
            return jsTipo + " " + id + ";\n";
        }
        return jsTipo + " " + id + " = " + value + ";\n";
    }

    @Override
    public String visitAsignacion(LanguageParser.AsignacionContext ctx) {
        String id = ctx.ID().getText();
        String value = visit(ctx.expr());
        return id + " = " + value + ";\n";
    }

    @Override
    public String visitExpr(LanguageParser.ExprContext ctx) {
        String result = visit(ctx.termino(0));
        for (int i = 1; i < ctx.termino().size(); i++) {
            String op = ctx.getChild(2 * i - 1).getText();
            String jsOp = op.equals("(suma)") ? "+" : "-";
            result += " " + jsOp + " " + visit(ctx.termino(i));
        }
        return result;
    }

    @Override
    public String visitTermino(LanguageParser.TerminoContext ctx) {
        String result = visit(ctx.factor(0));
        for (int i = 1; i < ctx.factor().size(); i++) {
            String op = ctx.getChild(2 * i - 1).getText();
            String jsOp = op.equals("(mult)") ? "*" : "/";
            result += " " + jsOp + " " + visit(ctx.factor(i));
        }
        return result;
    }

    @Override
    public String visitFactor(LanguageParser.FactorContext ctx) {
        if (ctx.NUM() != null) return ctx.NUM().getText();
        if (ctx.STRING() != null) return ctx.STRING().getText();
        if (ctx.BOOLEAN() != null) return ctx.BOOLEAN().getText();
        if (ctx.ID() != null) return ctx.ID().getText();
        return "(" + visit(ctx.expr()) + ")";
    }

    @Override
    public String visitIf_estructura(LanguageParser.If_estructuraContext ctx) {
        StringBuilder sb = new StringBuilder();
        sb.append("if (").append(visit(ctx.condicional(0))).append(") ");
        sb.append(visit(ctx.bloque(0)));
        for (int i = 1; i < ctx.condicional().size(); i++) {
            sb.append(" else if (").append(visit(ctx.condicional(i))).append(") ");
            sb.append(visit(ctx.bloque(i)));
        }
        if (ctx.bloque().size() > ctx.condicional().size()) {
            sb.append(" else ").append(visit(ctx.bloque(ctx.bloque().size() - 1)));
        }
        return sb.toString();
    }

    @Override
    public String visitCondicional(LanguageParser.CondicionalContext ctx) {
        if (ctx.AND() != null) {
            return visit(ctx.condicional(0)) + " && " + visit(ctx.condicional(1));
        }
        if (ctx.OR() != null) {
            return visit(ctx.condicional(0)) + " || " + visit(ctx.condicional(1));
        }
        if (ctx.getChildCount() == 3 && "(".equals(ctx.getChild(0).getText())) {
            return "(" + visit(ctx.condicional(0)) + ")";
        }
        if (ctx.op != null) {
            String left = visit(ctx.expr(0));
            String right = visit(ctx.expr(1));
            String op;
            switch (ctx.op.getType()) {
                case LanguageLexer.MENORQUE: op = "<"; break;
                case LanguageLexer.MAYORQUE: op = ">"; break;
                case LanguageLexer.MENORIGUAL: op = "<="; break;
                case LanguageLexer.MAYORIGUAL: op = ">="; break;
                case LanguageLexer.IGUAL: op = "=="; break;
                case LanguageLexer.DIFERENTE: op = "!="; break;
                default: op = "??"; break;
            }
            return left + " " + op + " " + right;
        }
        return "";
    }

    @Override
    public String visitBloque(LanguageParser.BloqueContext ctx) {
        StringBuilder sb = new StringBuilder();
        sb.append("{\n");
        for (LanguageParser.InstruccionContext var : ctx.instruccion()) {
            sb.append(visit(var));
        }
        sb.append("}\n");
        return sb.toString();
    }

    @Override
    @SuppressWarnings("StringConcatenationInsideStringBufferAppend")
    public String visitFor_estructura(LanguageParser.For_estructuraContext ctx) {
        StringBuilder sb = new StringBuilder();
        String init = "";
        String cond = "";
        String inc = "";

        // Solo soporta la forma: Recorre (ID; condicional; asignacion)
        // La declaración debe estar fuera del for en JS si ya fue declarada
        if (ctx.ID() != null) {
            init = ctx.ID().getText();
        }

        if (ctx.condicional() != null) {
            cond = visit(ctx.condicional());
        }

        if (ctx.asignacion() != null && !ctx.asignacion().isEmpty()) {
            inc = visit(ctx.asignacion(0));
            if (inc.endsWith(";\n")) inc = inc.substring(0, inc.length() - 2);
        }

        sb.append("for (" + init + "; " + cond + "; " + inc + ") " + visit(ctx.bloque()));
        return sb.toString();
    }

    @Override
    public String visitPrint_instr(LanguageParser.Print_instrContext ctx) {
        return "console.log(" + visit(ctx.expr()) + ");\n";
    }
}
