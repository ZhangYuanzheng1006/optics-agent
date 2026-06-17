import com.comsol.model.*;
import com.comsol.model.util.*;

public class ResultsEvalExport {
  public static Model run() throws Exception {
    Model model = ModelUtil.create("Model");
    model.modelNode().create("comp1");
    model.geom().create("geom1", 2);
    model.geom("geom1").create("r1", "Rectangle");
    model.geom("geom1").feature("r1").set("size", new String[]{"1", "1"});
    model.geom("geom1").run();
    model.cpl().create("maxop1", "Maximum", "geom1");
    model.cpl("maxop1").selection().all();
    model.physics().create("c", "CoefficientFormPDE", "geom1");
    model.physics("c").feature("cfeq1").set("c", "1");
    model.physics("c").feature("cfeq1").set("a", "0");
    model.physics("c").feature("cfeq1").set("f", "1");
    model.physics("c").create("dir1", "DirichletBoundary", 1);
    model.physics("c").feature("dir1").selection().all();
    model.mesh().create("mesh1", "geom1");
    model.mesh("mesh1").run();
    model.study().create("std1");
    model.study("std1").create("stat", "Stationary");
    model.sol().create("sol1");
    model.sol("sol1").study("std1");
    model.sol("sol1").createAutoSequence("std1");
    model.sol("sol1").runAll();
    model.result().dataset().create("dset1", "Solution");
    model.result().dataset("dset1").set("solution", "sol1");
    model.result().numerical().create("gev1", "EvalGlobal");
    model.result().numerical("gev1").set("data", "dset1");
    model.result().numerical("gev1").set("expr", new String[]{"maxop1(u)"});
    model.result().table().create("tbl1", "Table");
    model.result().numerical("gev1").set("table", "tbl1");
    model.result().numerical("gev1").setResult();
    double[][] values = model.result().table("tbl1").getReal();
    if (values.length > 0 && values[0].length > 0) {
      System.out.println("RESULT_VALUE " + values[0][0]);
    }
    return model;
  }

  public static void main(String[] args) throws Exception {
    Model model = run();
    if (args.length > 0) model.save(args[0]);
    System.out.println("RESULTS_EVAL_EXPORT_OK");
  }
}
