package milenguaje;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;

import org.antlr.v4.runtime.CharStream;
import org.antlr.v4.runtime.CharStreams;
import org.antlr.v4.runtime.CommonTokenStream;

public class Main {

    private static final String EXTENSION = "pepsi";
    private static final String DIRBASE = "src/test/resources/"; 

    public static void main(String[] args) throws IOException {
        String files[] = args.length==0? new String[]{ "test." + EXTENSION } : args;
        System.out.println("Dirbase: " + DIRBASE);
        for (String file : files){
            System.out.println("START: " + file);

            CharStream in = CharStreams.fromFileName(DIRBASE + file); // Por aqui se lee el archivo, de aqui va tener que pasarse desde la interfaz grafica 
            LanguageLexer lexer = new LanguageLexer(in);
            CommonTokenStream tokens = new CommonTokenStream(lexer);
            LanguageParser parser = new LanguageParser(tokens);

            LanguageParser.ProgramContext tree = parser.program();
            
            LanguageCustomVisitor visitor = new LanguageCustomVisitor();
            visitor.visit(tree);

            // Traducción a Python
            LanguageToPythonVisitor pyVisitor = new LanguageToPythonVisitor();
            String pythonCode = pyVisitor.visit(tree);
            String outputFile = file.replaceAll("\\.pepsi$", ".py");
            Files.write(Paths.get(DIRBASE + outputFile), pythonCode.getBytes(StandardCharsets.UTF_8));
            System.out.println("Archivo Python generado: " + outputFile);

            // Traducción a JavaScript
            LanguageToJavaScriptVisitor jsVisitor = new LanguageToJavaScriptVisitor();
            String jsCode = jsVisitor.visit(tree);
            String jsOutputFile = file.replaceAll("\\.pepsi$", ".js");
            Files.write(Paths.get(DIRBASE + jsOutputFile), jsCode.getBytes(StandardCharsets.UTF_8));
            System.out.println("Archivo JavaScript generado: " + jsOutputFile);

            System.out.println("FINISH: " + file);
        }
    }
}
