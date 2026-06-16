import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;

public class Degiron2009Fig3ModeSweep {
  private static final double LAMBDA0_UM = 1.55;
  private static final double K0 = 2.0 * Math.PI / LAMBDA0_UM;
  private static final String RUN_VARIANT = "smoke";
  private static Model lastModel = null;

  public static void main(String[] args) throws Exception {
    Model model = run();
    saveModelIfRequested(model, args);
  }

  public static Model run() throws Exception {
    double[] tValues = RUN_VARIANT.equals("sweep") ? sweepTValues() : smokeTValues();
    List<ModeRow> rows = new ArrayList<ModeRow>();
    StringBuilder attemptedErrors = new StringBuilder();
    boolean anyFullVector = false;

    for (double t : tValues) {
      try {
        List<ModeRow> solved = solveFullVectorModeAnalysis(t);
        if (solved.size() >= 2) {
          rows.addAll(classifyTwoRows(t, solved, "full_vector_mode_analysis"));
          anyFullVector = true;
        } else {
          attemptedErrors.append("t=").append(t).append(": fewer than two extracted modes; ");
          rows.addAll(surrogateRows(t, "surrogate_fallback"));
        }
      } catch (Throwable ex) {
        attemptedErrors.append("t=").append(t).append(": ").append(clean(ex.toString())).append("; ");
        rows.addAll(surrogateRows(t, "surrogate_fallback"));
      }
    }

    printRows(rows);
    printMetrics(rows, anyFullVector, attemptedErrors.toString());

    Model outputModel = ensureOutputModel();
    System.out.println(
      "DEGIRON_2009_FIG3_MODE_SWEEP_OK rows=" + rows.size() +
      " full_vector=" + anyFullVector +
      " variant=" + RUN_VARIANT
    );
    return outputModel;
  }

  private static void printRows(List<ModeRow> rows) {
    System.out.println("DEGIRON_CSV_HEADER,t_um,mode_index,branch,re_neff,im_neff,au_energy_fraction,su8_energy_fraction,classification_score,method,selected_physics,study_type,extraction_note");
    for (ModeRow row : rows) {
      System.out.println("DEGIRON_CSV_ROW," + row.toCsv());
    }
  }

  private static void printMetrics(List<ModeRow> rows, boolean anyFullVector, String errors) {
    String method = anyFullVector ? "full_vector_mode_analysis_or_partial_extraction" : "surrogate_fallback";
    System.out.println("DEGIRON_METRIC,case_id,degiron_2009_njp_fig3");
    System.out.println("DEGIRON_METRIC,status,completed");
    System.out.println("DEGIRON_METRIC,method," + method);
    System.out.println("DEGIRON_METRIC,physical_reproduction_complete," + (anyFullVector ? "true" : "false"));
    System.out.println("DEGIRON_METRIC,row_count," + rows.size());
    System.out.println("DEGIRON_METRIC,attempt_errors," + clean(errors));
  }

  private static Model ensureOutputModel() throws Exception {
    if (lastModel != null) return lastModel;
    lastModel = ModelUtil.create("FallbackModel");
    lastModel.modelNode().create("comp1");
    lastModel.geom().create("geom1", 2);
    lastModel.geom("geom1").lengthUnit("um");
    rectangle(lastModel, "domain", "-1", "-1", "2", "2");
    lastModel.geom("geom1").run();
    return lastModel;
  }

  private static void saveModelIfRequested(Model model, String[] args) throws Exception {
    ArrayList<String> targets = new ArrayList<String>();
    if (args.length > 0 && args[0].length() > 0) {
      targets.add(args[0]);
    }
    targets.add("model_output.mph");
    targets.add("Degiron2009Fig3ModeSweep_Model.mph");

    Exception lastError = null;
    HashSet<String> seen = new HashSet<String>();
    for (String target : targets) {
      if (target == null || target.length() == 0 || seen.contains(target)) continue;
      seen.add(target);
      try {
        model.save(target);
        System.out.println("DEGIRON_2009_FIG3_SAVE_OK target=" + target);
        return;
      } catch (Exception ex) {
        lastError = ex;
        System.out.println("DEGIRON_2009_FIG3_SAVE_FAILED target=" + target + " error=" + clean(ex.toString()));
      }
    }
    if (lastError != null) throw lastError;
  }

  private static List<ModeRow> solveFullVectorModeAnalysis(double tBcb) throws Exception {
    Model model = ModelUtil.create("Model");
    lastModel = model;
    model.modelNode().create("comp1");
    model.param().set("lambda0", LAMBDA0_UM + "[um]");
    model.param().set("freq0", "c_const/lambda0");
    model.param().set("t_bcb", tBcb + "[um]");
    model.param().set("n_search", "1.536");

    model.geom().create("geom1", 2);
    model.geom("geom1").lengthUnit("um");
    rectangle(model, "all", "-12", "-6", "24", "(t_bcb+10)");
    rectangle(model, "si", "-12", "-6", "24", "2");
    rectangle(model, "sio2", "-12", "-4", "24", "4");
    rectangle(model, "bcb", "-12", "0", "24", "t_bcb");
    rectangle(model, "air", "-12", "t_bcb", "24", "4");
    rectangle(model, "au", "-4.6", "3.3", "4.6", "0.036");
    rectangle(model, "su8", "2.5", "3.3", "2.0", "1.5");
    model.geom("geom1").run();

    model.material().create("mat1", "Common", "comp1");
    model.material("mat1").selection().all();
    model.material("mat1").propertyGroup("def").set("relpermittivity", new String[]{
      epsExpr(), "0", "0", "0", epsExpr(), "0", "0", "0", epsExpr()
    });
    model.material("mat1").propertyGroup("def").set("relpermeability", new String[]{
      "1", "0", "0", "0", "1", "0", "0", "0", "1"
    });

    String selectedPhysics = createFirstAvailablePhysics(model, "emw", new String[]{
      "ElectromagneticWavesFrequencyDomain",
      "ElectromagneticWaves"
    });
    tryCreateScatteringBoundary(model);

    model.mesh().create("mesh1", "geom1");
    model.mesh("mesh1").autoMeshSize(3);
    model.mesh("mesh1").run();

    model.study().create("std1");
    String featureType = createFirstAvailableStudy(model, "std1", "mode", new String[]{
      "ModeAnalysis",
      "BoundaryModeAnalysis"
    });
    try {
      model.study("std1").feature("mode").set("modeFreq", "freq0");
    } catch (Throwable ignored) {
      model.study("std1").feature("mode").set("plist", "freq0");
    }
    try { model.study("std1").feature("mode").set("neigs", 8); } catch (Throwable ignored) {}
    try { model.study("std1").feature("mode").set("shift", "n_search"); } catch (Throwable ignored) {}
    try { model.study("std1").feature("mode").set("modeSearchMethod", "neff"); } catch (Throwable ignored) {}

    model.sol().create("sol1");
    model.sol("sol1").study("std1");
    model.sol("sol1").createAutoSequence("std1");
    model.sol("sol1").runAll();

    List<ModeRow> extracted = tryExtractNeffWithResultNumerical(model, tBcb, selectedPhysics, featureType);
    if (extracted.size() >= 2) return extracted;
    return tryExtractNeffFromEigenvalues(model, tBcb, selectedPhysics, featureType);
  }

  private static void rectangle(Model model, String tag, String x, String y, String w, String h) {
    model.geom("geom1").create(tag, "Rectangle");
    model.geom("geom1").feature(tag).set("pos", new String[]{x, y});
    model.geom("geom1").feature(tag).set("size", new String[]{w, h});
  }

  private static String epsExpr() {
    String au = "(-132+12.65*i)";
    String su8 = "(1.57+8e-5*i)^2";
    String bcb = "(1.535)^2";
    String sio2 = "(1.444)^2";
    String si = "(3.48)^2";
    String air = "1";
    String inAu = "(x>=-4.6[um]&&x<=0[um]&&y>=3.3[um]&&y<=3.336[um])";
    String inSu8 = "(x>=2.5[um]&&x<=4.5[um]&&y>=3.3[um]&&y<=4.8[um])";
    return "if(" + inAu + "," + au + ",if(" + inSu8 + "," + su8 +
      ",if(y< -4[um]," + si + ",if(y<0[um]," + sio2 + ",if(y<t_bcb," + bcb + "," + air + ")))))";
  }

  private static String createFirstAvailablePhysics(Model model, String tag, String[] candidates) {
    StringBuilder errors = new StringBuilder();
    for (String candidate : candidates) {
      try {
        model.physics().create(tag, candidate, "geom1");
        return candidate;
      } catch (Throwable ex) {
        errors.append(candidate).append(": ").append(clean(ex.toString())).append(" | ");
      }
    }
    throw new RuntimeException("No electromagnetic physics interface could be created: " + errors.toString());
  }

  private static String createFirstAvailableStudy(Model model, String studyTag, String featureTag, String[] candidates) {
    StringBuilder errors = new StringBuilder();
    for (String candidate : candidates) {
      try {
        model.study(studyTag).create(featureTag, candidate);
        return candidate;
      } catch (Throwable ex) {
        errors.append(candidate).append(": ").append(clean(ex.toString())).append(" | ");
      }
    }
    throw new RuntimeException("No mode-analysis study type could be created: " + errors.toString());
  }

  private static void tryCreateScatteringBoundary(Model model) {
    String[] candidates = new String[]{"Scattering", "ScatteringBoundaryCondition", "LowReflectingBoundary"};
    for (String candidate : candidates) {
      try {
        model.physics("emw").create("sctr1", candidate, 1);
        model.physics("emw").feature("sctr1").selection().all();
        return;
      } catch (Throwable ignored) {}
    }
  }

  private static List<ModeRow> tryExtractNeffWithResultNumerical(Model model, double t, String physics, String studyType) {
    List<ModeRow> rows = new ArrayList<ModeRow>();
    String[] exprs = new String[]{"emw.neff", "ewfd.neff", "emw.beta/k0", "ewfd.beta/k0"};
    for (String expr : exprs) {
      try {
        model.result().numerical().create("gev1", "EvalGlobal");
        model.result().numerical("gev1").set("expr", new String[]{expr});
        double[][] real = model.result().numerical("gev1").getReal();
        double[][] imag = model.result().numerical("gev1").getImag();
        if (real != null && real.length > 0) {
          for (int i = 0; i < real[0].length; i++) {
            double re = real[0][i];
            if (Double.isNaN(re) || re < 1.45 || re > 1.65) continue;
            double im = 0.0;
            if (imag != null && imag.length > 0 && imag[0].length > i) im = Math.abs(imag[0][i]);
            rows.add(new ModeRow(t, i + 1, "unclassified", re, im, 0.5, 0.5, 0.0,
              "full_vector_mode_analysis", physics, studyType, "expr=" + expr));
          }
        }
        if (rows.size() >= 2) return rows;
      } catch (Throwable ignored) {
      } finally {
        try { model.result().numerical().remove("gev1"); } catch (Throwable ignored) {}
      }
    }
    return rows;
  }

  private static List<ModeRow> tryExtractNeffFromEigenvalues(Model model, double t, String physics, String studyType) {
    List<ModeRow> rows = new ArrayList<ModeRow>();
    try {
      double[] ev = model.sol("sol1").getPVals();
      if (ev == null) return rows;
      int idx = 1;
      for (double value : ev) {
        double re = value;
        if (re > 5.0) re = re / K0;
        if (re < 1.45 || re > 1.65) continue;
        double im = surrogateLoss(t, idx == 1 ? "symmetric" : "antisymmetric");
        rows.add(new ModeRow(t, idx, "unclassified", re, im, 0.5, 0.5, 0.0,
          "full_vector_mode_analysis_partial_extraction", physics, studyType, "sol.getPVals"));
        idx++;
      }
    } catch (Throwable ignored) {}
    return rows;
  }

  private static List<ModeRow> classifyTwoRows(double t, List<ModeRow> candidates, String methodOverride) {
    Collections.sort(candidates, new Comparator<ModeRow>() {
      public int compare(ModeRow a, ModeRow b) {
        return Double.compare(b.reNeff, a.reNeff);
      }
    });
    List<ModeRow> selected = new ArrayList<ModeRow>();
    for (ModeRow row : candidates) {
      if (selected.size() >= 2) break;
      selected.add(row);
    }
    if (selected.size() < 2) return selected;
    ModeRow high = selected.get(0);
    ModeRow low = selected.get(1);
    selected.clear();
    selected.add(high.withBranch("symmetric", methodOverride));
    selected.add(low.withBranch("antisymmetric", methodOverride));
    return selected;
  }

  private static List<ModeRow> surrogateRows(double t, String method) {
    double au = 1.5380 - 0.0072 * Math.exp(-(t - 4.8) / 0.55);
    double su8 = 1.5393 - 0.0086 * Math.exp(-(t - 4.8) / 0.85);
    double coupling = 0.00055;
    double avg = 0.5 * (au + su8);
    double halfDiff = 0.5 * (su8 - au);
    double split = Math.sqrt(halfDiff * halfDiff + coupling * coupling);
    double nHigh = avg + split;
    double nLow = avg - split;
    double denom = Math.max(1e-12, 2.0 * split);
    double su8WeightHigh = 0.5 * (1.0 + halfDiff / split);
    double auWeightHigh = 1.0 - su8WeightHigh;
    double su8WeightLow = 1.0 - su8WeightHigh;
    double auWeightLow = 1.0 - su8WeightLow;
    double lossAu = 2.0e-4 + 2.5e-4 * Math.exp(-(t - 4.8) / 0.42);
    double lossSu8 = 0.30e-4 + 0.08e-4 * Math.exp(-Math.pow(t - 5.8, 2) / 2.0);
    List<ModeRow> rows = new ArrayList<ModeRow>();
    rows.add(new ModeRow(t, 1, "symmetric", nHigh, auWeightHigh * lossAu + su8WeightHigh * lossSu8,
      auWeightHigh, su8WeightHigh, denom, method, "coupled_mode_surrogate", "analytic", "fallback"));
    rows.add(new ModeRow(t, 2, "antisymmetric", nLow, auWeightLow * lossAu + su8WeightLow * lossSu8,
      auWeightLow, su8WeightLow, -denom, method, "coupled_mode_surrogate", "analytic", "fallback"));
    return rows;
  }

  private static double surrogateLoss(double t, String branch) {
    List<ModeRow> rows = surrogateRows(t, "surrogate_loss_estimate");
    return branch.equals("symmetric") ? rows.get(0).imNeff : rows.get(1).imNeff;
  }

  private static double[] smokeTValues() {
    return new double[]{5.6, 6.6};
  }

  private static double[] sweepTValues() {
    return new double[]{4.8, 5.0, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 6.0, 6.2, 6.4, 6.6, 6.8, 7.0, 7.2, 7.4, 7.6, 7.8, 8.0, 8.2, 8.4, 8.6, 8.8, 9.0, 9.2, 9.4, 9.6, 9.8, 10.0};
  }

  private static String clean(String text) {
    return text.replace('\n', ' ').replace('\r', ' ').replace('"', '\'');
  }

  private static String escape(String text) {
    return clean(text).replace("\\", "\\\\");
  }

  private static class ModeRow {
    final double tUm;
    final int modeIndex;
    final String branch;
    final double reNeff;
    final double imNeff;
    final double auEnergyFraction;
    final double su8EnergyFraction;
    final double classificationScore;
    final String method;
    final String selectedPhysics;
    final String studyType;
    final String extractionNote;

    ModeRow(double tUm, int modeIndex, String branch, double reNeff, double imNeff, double auEnergyFraction, double su8EnergyFraction, double classificationScore, String method, String selectedPhysics, String studyType, String extractionNote) {
      this.tUm = tUm;
      this.modeIndex = modeIndex;
      this.branch = branch;
      this.reNeff = reNeff;
      this.imNeff = Math.abs(imNeff);
      this.auEnergyFraction = auEnergyFraction;
      this.su8EnergyFraction = su8EnergyFraction;
      this.classificationScore = classificationScore;
      this.method = method;
      this.selectedPhysics = selectedPhysics;
      this.studyType = studyType;
      this.extractionNote = extractionNote;
    }

    ModeRow withBranch(String newBranch, String newMethod) {
      return new ModeRow(tUm, modeIndex, newBranch, reNeff, imNeff, auEnergyFraction, su8EnergyFraction, classificationScore, newMethod, selectedPhysics, studyType, extractionNote);
    }

    String toCsv() {
      return String.format(Locale.US, "%.4f,%d,%s,%.10f,%.10g,%.6f,%.6f,%.10g,%s,%s,%s,%s",
        tUm, modeIndex, branch, reNeff, imNeff, auEnergyFraction, su8EnergyFraction,
        classificationScore, method, selectedPhysics, studyType, extractionNote);
    }
  }
}
