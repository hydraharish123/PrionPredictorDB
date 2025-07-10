const Protein = require("./../models/proteinModel");
const catchAsync = require("./../utils/catchAsync");
const APIFeatures = require("./../utils/apiFeatures");
const AppError = require("../utils/appError");
const File = require("../models/fileModel");

exports.getAllPrions = catchAsync(async (req, res, next) => {
  const features = new APIFeatures(Protein.find(), req.query)
    .filter()
    .sort()
    .limitFields()
    .paginate();

  const proteins = await features.query;
  const aggregating_like = proteins.filter(
    (p) => p["Aggregating-like"] === "Yes"
  ).length;

  const totalDocs = await Protein.countDocuments(features.filterQuery);
  const totalPages = Math.ceil(totalDocs / (req.params.page || 25));

  res.status(200).json({
    message: "Success",
    result: proteins.length,
    aggregating: aggregating_like,
    totalPage: totalPages,
    data: {
      data: proteins,
    },
  });
});

exports.getPrion = catchAsync(async (req, res, next) => {
  console.log(req.params);
  if (!req.params.id) return next(new AppError("No protein ID specified", 500));

  const prion = await Protein.find({
    uniprot_id: { $eq: req.params.id },
  }).select("-__v");
  const fileData = await File.find({
    uniprot_id: { $eq: req.params.id },
  }).select("-__v");

  if (!prion || !fileData)
    return next(new AppError("No document found with this protein ID", 501));

  res.status(200).json({
    message: "Success",
    data: {
      data: prion,
      files: fileData,
    },
  });
});
