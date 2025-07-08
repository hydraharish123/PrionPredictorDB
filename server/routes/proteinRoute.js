const express = require("express");
const proteinController = require("./../controllers/proteinController");

const router = express.Router();

router.route("/").get(proteinController.getAllPrions);
router.route("/:id").get(proteinController.getPrion);

module.exports = router;
