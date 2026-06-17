import com.comsol.model.*;
import com.comsol.model.util.*;

public class MeshFreeTri {
  public static Model run() throws Exception {
    Model model = ModelUtil.create("Model");
    model.modelNode().create("comp1");
    model.geom().create("geom1", 2);
    model.geom("geom1").lengthUnit("um");
    model.geom("geom1").create("r1", "Rectangle");
    model.geom("geom1").feature("r1").set("size", new String[]{"2", "1"});
    model.geom("geom1").run();
    model.mesh().create("mesh1", "geom1");
    model.mesh("mesh1").automatic(false);
    model.mesh("mesh1").feature().create("size1", "Size");
    model.mesh("mesh1").feature("size1").set("hmax", "0.1");
    model.mesh("mesh1").feature("size1").set("hmin", "0.01");
    model.mesh("mesh1").feature().create("ftri1", "FreeTri");
    model.mesh("mesh1").run();
    System.out.println("MESH_ELEMENTS " + model.mesh("mesh1").getNumElem());
    return model;
  }

  public static void main(String[] args) throws Exception {
    Model model = run();
    if (args.length > 0) model.save(args[0]);
    System.out.println("MESH_FREE_TRI_OK");
  }
}
