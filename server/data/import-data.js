const dotenv = require("dotenv");
const mongoose = require("mongoose");
const fs = require("fs");
const Protein = require("./../models/proteinModel");

dotenv.config({ path: "./../config.env" });

const DB = process.env.DATABASE.replace(
  "<PASSWORD>",
  process.env.DATABASE_PASSWORD
);

mongoose.connect(DB).then((con) => {
  console.log("DB connection successfull");
});

const prions = JSON.parse(fs.readFileSync(`${__dirname}/PPDB.json`, "utf-8"));

const importData = async () => {
  try {
    await Protein.create(prions);
    console.log("Data loaded");
  } catch (err) {
    console.log(err);
  }
  process.exit();
};
const deleteData = async () => {
  try {
    await Protein.deleteMany();
    console.log("Data deleted");
  } catch (err) {
    console.log(err);
  }
  process.exit();
};

if (process.argv[2] == "--import") {
  importData();
} else if (process.argv[2] == "--delete") {
  deleteData();
}
