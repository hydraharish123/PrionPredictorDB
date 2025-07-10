const mongoose = require("mongoose");

const fileSchema = new mongoose.Schema({
  uniprot_id: {
    type: String,
    unique: [true, "Protein ID should be unique"],
  },
  a3d_png: String,
  a3d_csv: String,
  pdb: String,
  centroids: String,
  clustering: String,
});

const File = mongoose.model("File", fileSchema);

module.exports = File;
