import com.comsol.model.*;
import com.comsol.model.util.*;

public class GeometrySequence {
  public static Model run() throws Exception {
    Model model = ModelUtil.create("Model");
    model.modelNode().create("comp1");
    model.geom().create("geom1", 2);
    model.geom("geom1").lengthUnit("um");
    model.geom("geom1").create("box", "Rectangle");
    model.geom("geom1").feature("box").set("size", new String[]{"4", "2"});
    model.geom("geom1").feature("box").set("pos", new String[]{"-2", "-1"});
    model.geom("geom1").create("hole", "Circle");
    model.geom("geom1").feature("hole").set("r", "0.4");
    model.geom("geom1").feature("hole").set("pos", new String[]{"0", "0"});
    model.geom("geom1").create("cut", "Difference");
    model.geom("geom1").feature("cut").selection("input").set("box");
    model.geom("geom1").feature("cut").selection("input2").set("hole");
    model.geom("geom1").feature("cut").set("keep", "off");
    model.geom("geom1").run();
    return model;
  }

  public static void main(String[] args) throws Exception {
    Model model = run();
    if (args.length > 0) model.save(args[0]);
    System.out.println("GEOMETRY_SEQUENCE_OK");
  }
}
