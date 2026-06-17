import com.comsol.model.*;
import com.comsol.model.util.*;

public class BatchSafeModel {
  public static Model run() throws Exception {
    Model model = ModelUtil.create("Model");
    model.modelNode().create("comp1");
    model.param().set("w", "1[um]");
    model.geom().create("geom1", 2);
    model.geom("geom1").lengthUnit("um");
    model.geom("geom1").create("r1", "Rectangle");
    model.geom("geom1").feature("r1").set("size", new String[]{"w", "w"});
    model.geom("geom1").run();
    model.mesh().create("mesh1", "geom1");
    model.mesh("mesh1").autoMeshSize(5);
    model.mesh("mesh1").run();
    return model;
  }

  public static void main(String[] args) throws Exception {
    Model model = run();
    if (args.length > 0) model.save(args[0]);
  }
}
