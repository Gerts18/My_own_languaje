package milenguaje;

public class LanguageToPythonVisitor extends LanguageBaseVisitor<String> {
    private final StringBuilder sb = new StringBuilder();
    private int indentLevel = 0;

    private void appendLine(String line) {
        for (int i = 0; i < indentLevel; i++) sb.append("    ");
        sb.append(line).append("\n");
    }

    @Override
    public String visitProgram(LanguageParser.ProgramContext ctx) {
        for (LanguageParser.InstruccionContext var : ctx.instruccion()) {
            String code = visit(var);
            if (code != null && !code.isEmpty()) sb.append(code);
        }
        return sb.toString();
    }

    @Override
    public String visitDeclaracion(LanguageParser.DeclaracionContext ctx) {
        String varName = ctx.ID().getText();
        String value = ctx.expr() != null ? visit(ctx.expr()) : "None";
        appendLine(varName + " = " + value);
        return "";
    }

    @Override
    public String visitAsignacion(LanguageParser.AsignacionContext ctx) {
        String varName = ctx.ID().getText();
        String value = visit(ctx.expr());
        appendLine(varName + " = " + value);
        return "";
    }

    @Override
    public String visitPrint_instr(LanguageParser.Print_instrContext ctx) {
        String value = visit(ctx.expr());
        appendLine("print(" + value + ")");
        return "";
    }

    @Override
    public String visitIf_estructura(LanguageParser.If_estructuraContext ctx) {
        int nConds = ctx.condicional().size();
        int nBlocks = ctx.bloque().size();

        // SoloSi
        String cond = visit(ctx.condicional(0));
        appendLine("if " + cond + ":");
        indentLevel++;
        appendBlock(ctx.bloque(0));
        indentLevel--;

        // SoloSiTamb
        for (int i = 1; i < nConds; i++) {
            cond = visit(ctx.condicional(i));
            appendLine("elif " + cond + ":");
            indentLevel++;
            appendBlock(ctx.bloque(i));
            indentLevel--;
        }

        // SiNo
        if (nBlocks > nConds) {
            appendLine("else:");
            indentLevel++;
            appendBlock(ctx.bloque(nBlocks - 1));
            indentLevel--;
        }
        return "";
    }

    private void appendBlock(LanguageParser.BloqueContext ctx) {
        for (LanguageParser.InstruccionContext var : ctx.instruccion()) {
            String code = visit(var);
            if (code != null && !code.isEmpty()) sb.append(code);
        }
    }

    @Override
    public String visitBloque(LanguageParser.BloqueContext ctx) {
        // Los bloques se manejan en appendBlock
        return "";
    }

    @Override
    public String visitFor_estructura(LanguageParser.For_estructuraContext ctx) {
        String varName = null;
        String start = null, end = null, step = null;
        boolean isClassicFor = false;

        // Inicialización: puede ser declaracion, asignacion o solo ID
        if (ctx.declaracion() != null) {
            varName = ctx.declaracion().ID().getText();
            start = visit(ctx.declaracion().expr());
        } else if (ctx.asignacion() != null && !ctx.asignacion().isEmpty()) {
            varName = ctx.asignacion(0).ID().getText();
            start = visit(ctx.asignacion(0).expr());
        } else if (ctx.ID() != null) {
            varName = ctx.ID().getText();
            start = varName;
        }

        // Condición
        if (ctx.condicional() != null) {
            LanguageParser.CondicionalContext condCtx = ctx.condicional();
            if (condCtx.expr() != null && condCtx.expr().size() == 2
                && condCtx.op != null
                && (condCtx.op.getType() == LanguageLexer.MENORQUE
                    || condCtx.op.getType() == LanguageLexer.MAYORQUE
                    || condCtx.op.getType() == LanguageLexer.MENORIGUAL
                    || condCtx.op.getType() == LanguageLexer.MAYORIGUAL)) {
                String left = visit(condCtx.expr(0));
                String right = visit(condCtx.expr(1));
                if (left.equals(varName)) {
                    end = right;
                }
            }
        }

        // Incremento
        if (ctx.asignacion() != null && ctx.asignacion().size() == 2) {
            LanguageParser.AsignacionContext incCtx = ctx.asignacion(1);
            String incVar = incCtx.ID().getText();
            if (incVar.equals(varName) && incCtx.expr() instanceof LanguageParser.ExprContext) {
                LanguageParser.ExprContext exprCtx = (LanguageParser.ExprContext) incCtx.expr();
                if (exprCtx.termino().size() == 2) {
                    String left = visit(exprCtx.termino(0));
                    String op = exprCtx.getChild(1).getText();
                    String right = visit(exprCtx.termino(1));
                    if (left.equals(varName) && (op.equals("(suma)") || op.equals("(resta)"))) {
                        step = op.equals("(suma)") ? right : "-" + right;
                        isClassicFor = (start != null && end != null && step != null);
                    }
                }
            }
        }

        // Si es un for clásico, usar for ... in range(...)
        if (isClassicFor && varName != null && start != null && end != null && step != null) {
            String rangeArgs = start + ", " + end;
            if (!"1".equals(step)) {
                rangeArgs += ", " + step;
            }
            appendLine("for " + varName + " in range(" + rangeArgs + "):");
            indentLevel++;
            appendBlock(ctx.bloque());
            indentLevel--;
            return "";
        }

        // Traducción forzada si no es clásico
        if (varName == null) varName = "i";
        if (start == null) start = "0";
        if (end == null) end = "10";
        if (step == null) step = "1";
        String rangeArgs = start + ", " + end;
        if (!"1".equals(step)) {
            rangeArgs += ", " + step;
        }
        appendLine("for " + varName + " in range(" + rangeArgs + "):");
        indentLevel++;
        appendBlock(ctx.bloque());
        indentLevel--;
        return "";
    }

    @Override
    public String visitCondicional(LanguageParser.CondicionalContext ctx) {
        if (ctx.AND() != null) {
            return visit(ctx.condicional(0)) + " and " + visit(ctx.condicional(1));
        }
        if (ctx.OR() != null) {
            return visit(ctx.condicional(0)) + " or " + visit(ctx.condicional(1));
        }
        if (ctx.getChildCount() == 3 && "(".equals(ctx.getChild(0).getText())) {
            return "(" + visit(ctx.condicional(0)) + ")";
        }
        if (ctx.op != null) {
            String left = visit(ctx.expr(0));
            String right = visit(ctx.expr(1));
            switch (ctx.op.getType()) {
                case LanguageLexer.MENORQUE: return left + " < " + right;
                case LanguageLexer.MAYORQUE: return left + " > " + right;
                case LanguageLexer.MENORIGUAL: return left + " <= " + right;
                case LanguageLexer.MAYORIGUAL: return left + " >= " + right;
                case LanguageLexer.IGUAL: return left + " == " + right;
                case LanguageLexer.DIFERENTE: return left + " != " + right;
                default: return left + " ?? " + right;
            }
        }
        return "";
    }

    @Override
    public String visitExpr(LanguageParser.ExprContext ctx) {
        String result = visit(ctx.termino(0));
        for (int i = 1; i < ctx.termino().size(); i++) {
            String op = ctx.getChild(2 * i - 1).getText();
            String term = visit(ctx.termino(i));
            if (op.equals("(suma)")) result += " + " + term;
            else if (op.equals("(resta)")) result += " - " + term;
        }
        return result;
    }

    @Override
    public String visitTermino(LanguageParser.TerminoContext ctx) {
        String result = visit(ctx.factor(0));
        for (int i = 1; i < ctx.factor().size(); i++) {
            String op = ctx.getChild(2 * i - 1).getText();
            String factor = visit(ctx.factor(i));
            if (op.equals("(mult)")) result += " * " + factor;
            else if (op.equals("(div)")) result += " / " + factor;
        }
        return result;
    }

    @Override
    public String visitFactor(LanguageParser.FactorContext ctx) {
        if (ctx.NUM() != null) return ctx.NUM().getText();
        if (ctx.STRING() != null) return ctx.STRING().getText();
        if (ctx.BOOLEAN() != null) return ctx.BOOLEAN().getText().equals("true") ? "True" : "False";
        if (ctx.ID() != null) return ctx.ID().getText();
        if (ctx.expr() != null) return "(" + visit(ctx.expr()) + ")";
        return "";
    }
}
