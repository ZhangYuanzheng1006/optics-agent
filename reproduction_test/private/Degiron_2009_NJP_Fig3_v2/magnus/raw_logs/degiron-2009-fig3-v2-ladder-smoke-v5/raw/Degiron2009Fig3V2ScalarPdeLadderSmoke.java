import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;

public class Degiron2009Fig3V2ScalarPdeLadderSmoke {
  private static final double LAMBDA0_UM = 1.55;
  private static final double K0 = 2.0 * Math.PI / LAMBDA0_UM;
  private static Model lastModel = null;

  public static Model run() throws Exception {
    ArrayList<String> rows = new ArrayList<String>();
    runCase(rows, "isolated_su8", 5.6, false, true);
    runCase(rows, "isolated_su8", 6.6, false, true);
    runCase(rows, "isolated_au", 5.6, true, false);
    runCase(rows, "isolated_au", 6.6, true, false);
    runCase(rows, "coupled", 5.4, true, true);
    runCase(rows, "coupled", 5.6, true, true);
    runCase(rows, "coupled", 6.6, true, true);
    printRows(rows);
    System.out.println("DEGIRON_2009_FIG3_V2_LADDER_SMOKE_OK rows=" + rows.size() + " method=scalar_tm_hx_pde");
    if (lastModel == null) {
      lastModel = buildModel("coupled", 5.6, true, true);
    }
    return lastModel;
  }

  public static void main(String[] args) throws Exception {
    Model model = run();
    if (args.length > 0 && args[0].length() > 0) {
      model.save(args[0]);
    }
  }

  private static void runCase(ArrayList<String> rows, String caseName, double t, boolean includeAu, boolean includeSu8) {
    try {
      Model model = buildModel(caseName, t, includeAu, includeSu8);
      lastModel = model;
      ArrayList<double[]> modes = extractModes(model);
      int kept = 0;
      for (int i = 0; i < modes.size(); i++) {
        double[] m = modes.get(i);
        boolean plausible = (m[1] >= 1.45 && m[1] <= 1.65 && m[2] <= 5.0e-2);
        String branch = branchName(caseName, kept);
        if (!plausible) branch = branch + "_raw";
        rows.add(csv(caseName, t, kept + 1, branch, m[1], m[2], m[3], m[4], "scalar_tm_hx_pde"));
        kept++;
        if (kept >= 8) break;
      }
      if (kept == 0) {
        System.out.println("DEGIRON_V2_ERROR," + caseName + "," + fmt(t) + ",no_filtered_modes");
      }
    } catch (Throwable ex) {
      System.out.println("DEGIRON_V2_ERROR," + caseName + "," + fmt(t) + "," + clean(ex.toString()));
    }
  }

  private static Model buildModel(String caseName, double tBcb, boolean includeAu, boolean includeSu8) throws Exception {
    Model model = ModelUtil.create("Model");
    model.modelNode().create("comp1");
    model.param().set("lambda0", LAMBDA0_UM + "[um]");
    model.param().set("k0", "2*pi/lambda0");
    model.param().set("t_bcb", tBcb + "[um]");
    model.param().set("shift_beta2", "-(2*pi/lambda0)^2*(1.536)^2");

    model.geom().create("geom1", 2);
    model.geom("geom1").lengthUnit("um");
    rectangle(model, "all", "-8", "-4", "16", "(t_bcb+6)");
    rectangle(model, "sio2", "-8", "-4", "16", "4");
    rectangle(model, "bcb", "-8", "0", "16", "t_bcb");
    rectangle(model, "air", "-8", "t_bcb", "16", "2");
    if (includeAu) rectangle(model, "au", "-4.6", "3.3", "4.6", "0.036");
    if (includeSu8) rectangle(model, "su8", "2.5", "3.3", "2.0", "1.5");
    model.geom("geom1").run();

    model.variable().create("var1");
    model.variable("var1").model("comp1");
    model.variable("var1").set("epsr", epsExpr(includeAu, includeSu8));

    model.physics().create("c", "CoefficientFormPDE", "geom1");
    model.physics("c").feature("cfeq1").set("c", "1/epsr");
    model.physics("c").feature("cfeq1").set("a", "-k0^2");
    model.physics("c").feature("cfeq1").set("da", "1/epsr");
    model.physics("c").feature("cfeq1").set("f", "0");
    model.physics("c").create("dir1", "DirichletBoundary", 1);
    model.physics("c").feature("dir1").selection().all();

    model.mesh().create("mesh1", "geom1");
    model.mesh("mesh1").automatic(false);
    model.mesh("mesh1").feature().create("size1", "Size");
    model.mesh("mesh1").feature("size1").set("hmax", includeAu ? "0.09" : "0.16");
    model.mesh("mesh1").feature("size1").set("hmin", includeAu ? "0.006" : "0.02");
    try {
      model.mesh("mesh1").feature().create("ftri_user", "FreeTri");
    } catch (Throwable ignored) {
    }
    model.mesh("mesh1").run();

    model.study().create("std1");
    model.study("std1").create("eig", "Eigenvalue");
    model.study("std1").feature("eig").set("neigs", includeAu ? 16 : 10);
    model.study("std1").feature("eig").set("shift", "shift_beta2");
    try {
      model.study("std1").feature("eig").set("rtol", "1e-5");
    } catch (Throwable ignored) {
    }

    model.sol().create("sol1");
    model.sol("sol1").study("std1");
    model.sol("sol1").createAutoSequence("std1");
    model.sol("sol1").runAll();
    return model;
  }

  private static void rectangle(Model model, String tag, String x, String y, String w, String h) {
    model.geom("geom1").create(tag, "Rectangle");
    model.geom("geom1").feature(tag).set("pos", new String[]{x, y});
    model.geom("geom1").feature(tag).set("size", new String[]{w, h});
  }

  private static String epsExpr(boolean includeAu, boolean includeSu8) {
    String expr = "if(y<0[um],(1.444)^2,if(y<t_bcb,(1.535)^2,1))";
    if (includeSu8) {
      expr = "if((x>=2.5[um]&&x<=4.5[um]&&y>=3.3[um]&&y<=4.8[um]),(1.57+8e-5*i)^2," + expr + ")";
    }
    if (includeAu) {
      expr = "if((x>=-4.6[um]&&x<=0[um]&&y>=3.3[um]&&y<=3.336[um]),(-132+12.65*i)," + expr + ")";
    }
    return expr;
  }

  private static ArrayList<double[]> extractModes(Model model) {
    ArrayList<double[]> modes = new ArrayList<double[]>();
    double[] lr = model.sol("sol1").getPVals();
    double[] li = null;
    try { li = model.sol("sol1").getPValsImag(); } catch (Throwable ignored) {}
    if (lr == null) return modes;
    for (int i = 0; i < lr.length; i++) {
      double im = (li != null && li.length > i) ? li[i] : 0.0;
      double[] beta = sqrtComplex(-lr[i], -im);
      double neffRe = beta[0] / K0;
      double neffIm = Math.abs(beta[1] / K0);
      modes.add(new double[]{i + 1, neffRe, neffIm, lr[i], im});
    }
    sortModes(modes);
    return modes;
  }

  private static void sortModes(ArrayList<double[]> modes) {
    for (int i = 0; i < modes.size(); i++) {
      for (int j = i + 1; j < modes.size(); j++) {
        if (modeScore(modes.get(j)) < modeScore(modes.get(i))) {
          double[] tmp = modes.get(i);
          modes.set(i, modes.get(j));
          modes.set(j, tmp);
        }
      }
    }
  }

  private static double modeScore(double[] mode) {
    return Math.abs(mode[1] - 1.536) + 10.0 * mode[2];
  }

  private static String branchName(String caseName, int idx) {
    if (caseName.equals("isolated_su8")) return "isolated_su8_mode_" + (idx + 1);
    if (caseName.equals("isolated_au")) return "isolated_au_mode_" + (idx + 1);
    if (idx == 0) return "coupled_candidate_1";
    if (idx == 1) return "coupled_candidate_2";
    return "coupled_extra_" + (idx + 1);
  }

  private static double[] sqrtComplex(double ar, double ai) {
    double r = Math.sqrt(ar * ar + ai * ai);
    double real = Math.sqrt(Math.max(0.0, (r + ar) / 2.0));
    double imag = Math.sqrt(Math.max(0.0, (r - ar) / 2.0));
    if (ai < 0) imag = -imag;
    if (real < 0) {
      real = -real;
      imag = -imag;
    }
    return new double[]{real, imag};
  }

  private static String csv(String caseName, double t, int modeIndex, String branch, double reNeff, double imNeff, double lambdaRe, double lambdaIm, String method) {
    return caseName + "," + fmt(t) + "," + modeIndex + "," + branch + "," + fmt10(reNeff) + "," + fmt10(imNeff) + "," + fmt10(lambdaRe) + "," + fmt10(lambdaIm) + "," + method + ",dirichlet_finite_window,lambda_equals_minus_beta_squared";
  }

  private static void printRows(ArrayList<String> rows) {
    System.out.println("DEGIRON_V2_CSV_HEADER,case_name,t_um,mode_index,branch,re_neff,im_neff,lambda_re,lambda_im,method,boundary,extraction_note");
    for (int i = 0; i < rows.size(); i++) {
      System.out.println("DEGIRON_V2_CSV_ROW," + rows.get(i));
    }
  }

  private static String fmt(double v) {
    return String.format(Locale.US, "%.4f", v);
  }

  private static String fmt10(double v) {
    return String.format(Locale.US, "%.10g", v);
  }

  private static String clean(String text) {
    return text.replace('\n', ' ').replace('\r', ' ').replace(',', ';');
  }
}
