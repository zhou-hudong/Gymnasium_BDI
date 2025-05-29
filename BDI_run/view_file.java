
import java.io.FileInputStream;
import java.io.ObjectInputStream;
import java.util.Map;

public class view_file {
    private static final String FILE_PATH = "prova_lake.pkl";

    public static void main(String[] args) {
        try (FileInputStream fis = new FileInputStream(FILE_PATH);
             ObjectInputStream ois = new ObjectInputStream(fis)) {

            // legge un Object dal file，poi lo trasforma in Map<String, Double>
            Object obj = ois.readObject();
            if (!(obj instanceof Map)) {
                System.err.println("文件内容不是 Map 类型，而是: " + obj.getClass().getName());
                return;
            }

            @SuppressWarnings("unchecked")
            Map<String, Double> qtable = (Map<String, Double>) obj;

            // stampa size table
            System.out.println("Loaded Q-table entries: " + qtable.size());

            // stampa q table
            for (Map.Entry<String, Double> entry : qtable.entrySet()) {
                String key = entry.getKey();
                Double value = entry.getValue();
                System.out.printf("State,Action = %s → Q = %.6f%n", key, value);
            }

        } catch (Exception e) {
            System.err.println("deserializzazione fallita: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
