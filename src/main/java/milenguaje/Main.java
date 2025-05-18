package milenguaje;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;

import org.antlr.v4.runtime.CharStream;
import org.antlr.v4.runtime.CharStreams;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.BailErrorStrategy;
import org.antlr.v4.runtime.misc.ParseCancellationException;
import org.antlr.v4.runtime.RecognitionException;

public class Main {

    private static final String EXTENSION = "pepsi";
    private static final String DIRBASE   = "src/test/resources/";

    public static void main(String[] args) {
        String[] files = args.length == 0
            ? new String[]{ "test." + EXTENSION }
            : args;

        for (String file : files) {
            System.out.println("START: " + file);
            try {
                // 1) Leer el archivo de entrada
                CharStream in = CharStreams.fromFileName(DIRBASE + file);

                // 2) Crear lexer y stream de tokens
                LanguageLexer lexer = new LanguageLexer(in);
                lexer.removeErrorListeners();               // ← elimina el listener por defecto del lexer
                CommonTokenStream tokens = new CommonTokenStream(lexer);

                // 3) Crear parser y configurar “fail-fast”
                LanguageParser parser = new LanguageParser(tokens);
                parser.removeErrorListeners();              // elimina listener por defecto del parser
                parser.setErrorHandler(new BailErrorStrategy());
                parser.addErrorListener(ThrowingErrorListener.INSTANCE);

                // 4) Parsear
                LanguageParser.ProgramContext tree = parser.program();

                // 5) Ejecutar tu visitor
                new LanguageCustomVisitor().visit(tree);

                // 6) Traducir a Python
                String pyCode = new LanguageToPythonVisitor().visit(tree);
                String pyOut  = file.replaceAll("\\.pepsi$", ".py");
                Files.write(Paths.get(DIRBASE + pyOut),
                            pyCode.getBytes(StandardCharsets.UTF_8));
                System.out.println("Archivo Python generado: " + pyOut);

                // 7) Traducir a JavaScript
                String jsCode = new LanguageToJavaScriptVisitor().visit(tree);
                String jsOut  = file.replaceAll("\\.pepsi$", ".js");
                Files.write(Paths.get(DIRBASE + jsOut),
                            jsCode.getBytes(StandardCharsets.UTF_8));
                System.out.println("Archivo JavaScript generado: " + jsOut);

                System.out.println("FINISH: " + file);
                System.exit(0);

            } catch (ParseCancellationException | RecognitionException e) {
                // Sólo imprimimos el mensaje de tu ThrowingErrorListener
                System.err.println(e.getMessage());
                System.exit(1);
            } catch (IOException e) {
                System.err.println("I/O Error: " + e.getMessage());
                System.exit(2);
            }
        }
    }
}
