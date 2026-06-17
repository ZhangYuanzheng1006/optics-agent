import com.comsol.model.*;
import com.comsol.model.util.*;

public class StudySolverEigenvalue {
  public static Model run() throws Exception {
    Model model = ModelUtil.create("Model");
    // Generic Coefficient Form PDE eigenvalue template only.
    // Do not use this as a Wave Optics/RF mode-analysis model without GUI-exported Java validation.
    model.modelNode().create("comp1");
    model.geom().create("geom1", 2);
    model.geom("geom1").create("r1", "Rectangle");
    model.geom("geom1").feature("r1").set("size", new String[]{"1", "1"});
    model.geom("geom1").run();
    model.physics().create("c", "CoefficientFormPDE", "geom1");
    model.physics("c").feature("cfeq1").set("c", "1");
    model.physics("c").feature("cfeq1").set("a", "0");
    model.physics("c").feature("cfeq1").set("f", "0");
    model.physics("c").feature("cfeq1").set("da", "1");
    model.physics("c").create("dir1", "DirichletBoundary", 1);
    model.physics("c").feature("dir1").selection().all();
    model.mesh().create("mesh1", "geom1");
    model.mesh("mesh1").autoMeshSize(4);
    model.mesh("mesh1").run();
    model.study().create("std1");
    model.study("std1").create("eig", "Eigenvalue");
    model.study("std1").feature("eig").set("neigs", 4);
    model.study("std1").feature("eig").set("shift", "10");
    model.sol().create("sol1");
    model.sol("sol1").study("std1");
    model.sol("sol1").createAutoSequence("std1");
    model.sol("sol1").runAll();
    double[] evals = model.sol("sol1").getPVals();
    StringBuilder line = new StringBuilder();
    for (int i = 0; i < evals.length; i++) {
      if (i > 0) line.append(",");
      line.append(evals[i]);
    }
    System.out.println("EIGENVALUES " + line.toString());
    return model;
  }

  public static void main(String[] args) throws Exception {
    Model model = run();
    if (args.length > 0) model.save(args[0]);
    System.out.println("STUDY_SOLVER_EIGENVALUE_OK");
  }
}
