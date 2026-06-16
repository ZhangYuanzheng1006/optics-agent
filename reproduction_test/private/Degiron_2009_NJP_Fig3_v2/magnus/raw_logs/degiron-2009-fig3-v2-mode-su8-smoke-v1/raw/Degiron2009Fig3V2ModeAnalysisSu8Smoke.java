import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;

public class Degiron2009Fig3V2ModeAnalysisSu8Smoke {
  private static final double LAMBDA0_UM = 1.55;
  private static final double K0_SI = 2.0 * Math.PI / (LAMBDA0_UM * 1.0e-6);
  private static Model lastModel = null;

  public static Model run() throws Exception {
    double[] tValues = new double[]{5.6, 6.6};
    ArrayList<String> rows = new ArrayList<String>();
    for (int i = 0; i < tValues.length; i++) {
      runCase(rows, tValues[i]);
    }
    printRows(rows);
    System.out.println("DEGIRON_2009_FIG3_V2_MODE_SU8_SMOKE_OK rows=" + rows.size() + " method=wave_optics_mode_analysis_probe");
    if (lastModel == null) {
      lastModel = buildGeometryOnly(5.6);
    }
    return lastModel;
  }

  public static void main(String[] args) throws Exception {
    Model model = run();
    if (args.length > 0 && args[0].length() > 0) {
      model.save(args[0]);
    }
  }

  private static void runCase(ArrayList<String> rows, double tBcb) {
    StringBuilder errors = new StringBuilder();
    String[] shiftKinds = new String[]{"neff", "beta", "plain"};
    for (int i = 0; i < shiftKinds.length; i++) {
      try {
        Model model = buildAndSolve(tBcb, shiftKinds[i]);
        lastModel = model;
        ArrayList<double[]> modes = extractModes(model, shiftKinds[i]);
        if (modes.size() > 0) {
          int kept = 0;
          for (int j = 0; j < modes.size(); j++) {
            double[] m = modes.get(j);
            if (m[1] < 1.45 || m[1] > 1.65 || m[2] > 5.0e-2) {
              continue;
            }
            rows.add(csv("isolated_su8_mode", tBcb, kept + 1, "su8_candidate_" + (kept + 1), m[1], m[2], m[3], m[4], shiftKinds[i], modeNote((int)m[0])));
            kept++;
            if (kept >= 6) break;
          }
          if (kept > 0) return;
          errors.append("shift_kind=").append(shiftKinds[i]).append(": extracted modes outside plausibility range; ");
        } else {
          errors.append("shift_kind=").append(shiftKinds[i]).append(": no extractable modes; ");
        }
      } catch (Throwable ex) {
        errors.append("shift_kind=").append(shiftKinds[i]).append(": ").append(clean(ex.toString())).append("; ");
      }
    }
    System.out.println("DEGIRON_V2_ERROR,isolated_su8_mode," + fmt(tBcb) + "," + clean(errors.toString()));
  }

  private static Model buildAndSolve(double tBcb, String shiftKind) throws Exception {
    Model model = buildBaseModel(tBcb);
    createFirstAvailablePhysics(model, "emw", new String[]{
      "ElectromagneticWavesFrequencyDomain",
      "ElectromagneticWaves"
    });
    tryCreateScatteringBoundary(model);

    model.mesh().create("mesh1", "geom1");
    model.mesh("mesh1").automatic(false);
    model.mesh("mesh1").feature().create("size1", "Size");
    model.mesh("mesh1").feature("size1").set("hmax", "0.20");
    model.mesh("mesh1").feature("size1").set("hmin", "0.02");
    try {
      model.mesh("mesh1").feature().create("ftri_user", "FreeTri");
    } catch (Throwable ignored) {
    }
    model.mesh("mesh1").run();

    model.study().create("std1");
    createFirstAvailableStudy(model, "std1", "mode", new String[]{
      "ModeAnalysis",
      "BoundaryModeAnalysis"
    });
    setModeStudyProperties(model, shiftKind);

    model.sol().create("sol1");
    model.sol("sol1").study("std1");
    model.sol("sol1").createAutoSequence("std1");
    model.sol("sol1").runAll();
    return model;
  }

  private static Model buildBaseModel(double tBcb) throws Exception {
    Model model = ModelUtil.create("Model");
    lastModel = model;
    model.modelNode().create("comp1");
    model.param().set("lambda0", LAMBDA0_UM + "[um]");
    model.param().set("freq0", "c_const/lambda0");
    model.param().set("k0", "2*pi/lambda0");
    model.param().set("t_bcb", tBcb + "[um]");
    model.param().set("n_search", "1.536");
    model.param().set("beta_search", "k0*n_search");

    model.geom().create("geom1", 2);
    model.geom("geom1").lengthUnit("um");
    rectangle(model, "all", "-7", "-3", "14", "(t_bcb+6)");
    rectangle(model, "sio2", "-7", "-3", "14", "3");
    rectangle(model, "bcb", "-7", "0", "14", "t_bcb");
    rectangle(model, "air", "-7", "t_bcb", "14", "3");
    rectangle(model, "su8", "-1", "3.3", "2", "1.5");
    model.geom("geom1").run();

    model.material().create("mat1", "Common", "comp1");
    model.material("mat1").selection().all();
    model.material("mat1").propertyGroup("def").set("relpermittivity", new String[]{
      epsExpr(), "0", "0", "0", epsExpr(), "0", "0", "0", epsExpr()
    });
    model.material("mat1").propertyGroup("def").set("relpermeability", new String[]{
      "1", "0", "0", "0", "1", "0", "0", "0", "1"
    });
    return model;
  }

  private static Model buildGeometryOnly(double tBcb) throws Exception {
    Model model = buildBaseModel(tBcb);
    return model;
  }

  private static void setModeStudyProperties(Model model, String shiftKind) {
    try { model.study("std1").feature("mode").set("modeFreq", "freq0"); } catch (Throwable ignored) {}
    try { model.study("std1").feature("mode").set("plist", "freq0"); } catch (Throwable ignored) {}
    try { model.study("std1").feature("mode").set("neigs", 8); } catch (Throwable ignored) {}
    try { model.study("std1").feature("mode").set("ngen", 8); } catch (Throwable ignored) {}
    if ("neff".equals(shiftKind)) {
      try { model.study("std1").feature("mode").set("modeSearchMethod", "neff"); } catch (Throwable ignored) {}
      try { model.study("std1").feature("mode").set("shift", "n_search"); } catch (Throwable ignored) {}
    } else if ("beta".equals(shiftKind)) {
      try { model.study("std1").feature("mode").set("shift", "beta_search"); } catch (Throwable ignored) {}
    } else {
      try { model.study("std1").feature("mode").set("shift", "1.536"); } catch (Throwable ignored) {}
    }
  }

  private static void rectangle(Model model, String tag, String x, String y, String w, String h) {
    model.geom("geom1").create(tag, "Rectangle");
    model.geom("geom1").feature(tag).set("pos", new String[]{x, y});
    model.geom("geom1").feature(tag).set("size", new String[]{w, h});
  }

  private static String epsExpr() {
    String su8 = "(1.57+8e-5*i)^2";
    String bcb = "(1.535)^2";
    String sio2 = "(1.444)^2";
    String air = "1";
    String inSu8 = "(x>=-1[um]&&x<=1[um]&&y>=3.3[um]&&y<=4.8[um])";
    return "if(" + inSu8 + "," + su8 + ",if(y<0[um]," + sio2 + ",if(y<t_bcb," + bcb + "," + air + ")))";
  }

  private static String createFirstAvailablePhysics(Model model, String tag, String[] candidates) {
    StringBuilder errors = new StringBuilder();
    for (int i = 0; i < candidates.length; i++) {
      try {
        model.physics().create(tag, candidates[i], "geom1");
        return candidates[i];
      } catch (Throwable ex) {
        errors.append(candidates[i]).append(": ").append(clean(ex.toString())).append(" | ");
      }
    }
    throw new RuntimeException("No electromagnetic physics interface could be created: " + errors.toString());
  }

  private static String createFirstAvailableStudy(Model model, String studyTag, String featureTag, String[] candidates) {
    StringBuilder errors = new StringBuilder();
    for (int i = 0; i < candidates.length; i++) {
      try {
        model.study(studyTag).create(featureTag, candidates[i]);
        return candidates[i];
      } catch (Throwable ex) {
        errors.append(candidates[i]).append(": ").append(clean(ex.toString())).append(" | ");
      }
    }
    throw new RuntimeException("No mode-analysis study type could be created: " + errors.toString());
  }

  private static void tryCreateScatteringBoundary(Model model) {
    String[] candidates = new String[]{"Scattering", "ScatteringBoundaryCondition", "LowReflectingBoundary"};
    for (int i = 0; i < candidates.length; i++) {
      try {
        model.physics("emw").create("sctr1", candidates[i], 1);
        model.physics("emw").feature("sctr1").selection().all();
        return;
      } catch (Throwable ignored) {
      }
    }
  }

  private static ArrayList<double[]> extractModes(Model model, String shiftKind) {
    ArrayList<double[]> modes = new ArrayList<double[]>();
    appendResultExpressionModes(model, modes);
    if (modes.size() == 0) {
      appendRawEigenvalueModes(model, modes);
    }
    sortModes(modes);
    return modes;
  }

  private static void appendResultExpressionModes(Model model, ArrayList<double[]> modes) {
    String[] exprs = new String[]{"emw.neff", "ewfd.neff", "emw.beta/k0", "ewfd.beta/k0"};
    for (int e = 0; e < exprs.length; e++) {
      String tag = "gev" + e;
      try {
        model.result().dataset().create("dset1", "Solution");
        model.result().dataset("dset1").set("solution", "sol1");
      } catch (Throwable ignored) {
      }
      try {
        model.result().numerical().create(tag, "EvalGlobal");
        try { model.result().numerical(tag).set("data", "dset1"); } catch (Throwable ignored) {}
        model.result().numerical(tag).set("expr", new String[]{exprs[e]});
        double[][] real = model.result().numerical(tag).getReal();
        double[][] imag = model.result().numerical(tag).getImag();
        if (real != null && real.length > 0) {
          for (int i = 0; i < real[0].length; i++) {
            double re = real[0][i];
            double im = 0.0;
            if (imag != null && imag.length > 0 && imag[0].length > i) {
              im = Math.abs(imag[0][i]);
            }
            modes.add(new double[]{1000 + e * 100 + i + 1, re, im, re, im});
          }
        }
        if (modes.size() > 0) return;
      } catch (Throwable ignored) {
      } finally {
        try { model.result().numerical().remove(tag); } catch (Throwable ignored) {}
      }
    }
  }

  private static void appendRawEigenvalueModes(Model model, ArrayList<double[]> modes) {
    try {
      double[] lr = model.sol("sol1").getPVals();
      double[] li = null;
      try { li = model.sol("sol1").getPValsImag(); } catch (Throwable ignored) {}
      if (lr == null) return;
      for (int i = 0; i < lr.length; i++) {
        double reRaw = lr[i];
        double imRaw = (li != null && li.length > i) ? li[i] : 0.0;
        double[] neff = convertRawEigenvalueToNeff(reRaw, imRaw);
        modes.add(new double[]{i + 1, neff[0], Math.abs(neff[1]), reRaw, imRaw});
      }
    } catch (Throwable ignored) {
    }
  }

  private static double[] convertRawEigenvalueToNeff(double reRaw, double imRaw) {
    if (Math.abs(reRaw) >= 1.45 && Math.abs(reRaw) <= 1.65) {
      return new double[]{Math.abs(reRaw), Math.abs(imRaw)};
    }
    double betaAbs = Math.sqrt(reRaw * reRaw + imRaw * imRaw);
    if (betaAbs / K0_SI >= 1.45 && betaAbs / K0_SI <= 1.65) {
      return new double[]{betaAbs / K0_SI, 0.0};
    }
    double[] sqrt = sqrtComplex(-reRaw, -imRaw);
    return new double[]{sqrt[0] / K0_SI, Math.abs(sqrt[1] / K0_SI)};
  }

  private static double[] sqrtComplex(double ar, double ai) {
    double r = Math.sqrt(ar * ar + ai * ai);
    double real = Math.sqrt(Math.max(0.0, (r + ar) / 2.0));
    double imag = Math.sqrt(Math.max(0.0, (r - ar) / 2.0));
    if (ai < 0) imag = -imag;
    return new double[]{real, imag};
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

  private static String modeNote(int rawIndex) {
    if (rawIndex >= 1000) return "result_expression_neff_or_beta_over_k0";
    return "raw_eigenvalue_converted_heuristically";
  }

  private static String csv(String caseName, double t, int modeIndex, String branch, double reNeff, double imNeff, double rawRe, double rawIm, String shiftKind, String note) {
    return caseName + "," + fmt(t) + "," + modeIndex + "," + branch + "," + fmt10(reNeff) + "," + fmt10(imNeff) + "," + fmt10(rawRe) + "," + fmt10(rawIm) + ",wave_optics_mode_analysis_probe,scattering_or_default_boundary," + note + "_shift_" + shiftKind;
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
    return text.replace('\n', ' ').replace('\r', ' ').replace(',', ';').replace('"', '\'');
  }
}
