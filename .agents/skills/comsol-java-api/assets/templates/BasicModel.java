import com.comsol.model.*;
import com.comsol.model.util.*;

public class BasicModel {
  public static Model run() throws Exception {
    Model model = ModelUtil.create("Model");
    model.modelNode().create("comp1");
    model.param().set("L", "1[um]");
    model.param().set("W", "0.5[um]");
    model.geom().create("geom1", 2);
    model.geom("geom1").lengthUnit("um");
    model.geom("geom1").create("r1", "Rectangle");
    model.geom("geom1").feature("r1").set("size", new String[]{"L", "W"});
    model.geom("geom1").feature("r1").set("pos", new String[]{"-L/2", "-W/2"});
    model.geom("geom1").run();
    model.mesh().create("mesh1", "geom1");
    model.mesh("mesh1").autoMeshSize(4);
    model.mesh("mesh1").run();
    return model;
  }

  public static void main(String[] args) throws Exception {
    Model model = run();
    if (args.length > 0) model.save(args[0]);
    System.out.println("BASIC_MODEL_OK");
  }
}
