const mongoose = require("mongoose");

const proteinSchema = new mongoose.Schema(
  {
    uniprot_id: {
      type: String,
      unique: [true, "Protein ID should be unique"],
    },
    "Entry Name": String,
    "Protein Name": String,
    "Gene Names": String,
    Length: Number,
    Function: {
      type: String,
      default: "-",
    },
    Sequence: String,
    "GO Terms": String,
    "AlphaFold Model": String,
    SEQid: String,
    PRDstart: Number,
    PRDend: Number,
    PRDlen: Number,
    PRDaa: String,
    SASA: Number,
    Average_pLDDT: Number,
    "Aggregating-like": String,
  },
  {
    toJSON: { virtuals: true },
    toObject: { virtuals: true },
    id: false,
  }
);

const Protein = mongoose.model("Protein", proteinSchema);

module.exports = Protein;
