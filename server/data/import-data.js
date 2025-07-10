const dotenv = require("dotenv");
const mongoose = require("mongoose");
const fs = require("fs");
const Protein = require("./../models/proteinModel");
const File = require("./../models/fileModel");

dotenv.config({ path: "./../config.env" });

const DB = process.env.DATABASE.replace(
  "<PASSWORD>",
  process.env.DATABASE_PASSWORD
);

mongoose.connect(DB).then((con) => {
  console.log("DB connection successfull");
});

const files = JSON.parse(
  fs.readFileSync(`${__dirname}/file_paths.json`, "utf-8")
);

const importData = async () => {
  try {
    await File.create(files);
    console.log("Data loaded");
  } catch (err) {
    console.log(err);
  }
  process.exit();
};
const deleteData = async () => {
  try {
    await File.deleteMany();
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
