const express = require("express");
const multer = require("multer");
const fs = require("fs");
const axios = require("axios");
const cors = require("cors");

const app = express();
app.use(cors());

const upload = multer({ dest: "uploads/" });

// 🔐 CONFIGURE AQUI
const GITHUB_TOKEN = "SEU_TOKEN_GITHUB";
const REPO = "SEU_USUARIO/SEU_REPO";

// função upload github
async function uploadToGitHub(filePath, fileName) {
  const content = fs.readFileSync(filePath, { encoding: "base64" });

  const response = await axios.put(
    `https://api.github.com/repos/${REPO}/contents/uploads/${Date.now()}-${fileName}`,
    {
      message: "upload de prints via site",
      content: content
    },
    {
      headers: {
        Authorization: `token ${GITHUB_TOKEN}`
      }
    }
  );

  return response.data.content.download_url;
}

// rota upload
app.post("/upload", upload.fields([
  { name: "coupon" },
  { name: "deposit" }
]), async (req, res) => {
  try {
    const couponFile = req.files.coupon[0];
    const depositFile = req.files.deposit[0];

    const couponURL = await uploadToGitHub(couponFile.path, "coupon.png");
    const depositURL = await uploadToGitHub(depositFile.path, "deposit.png");

    res.json({
      success: true,
      couponURL,
      depositURL
    });

  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Erro no upload" });
  }
});

app.listen(3000, () => console.log("Servidor rodando na porta 3000"));
