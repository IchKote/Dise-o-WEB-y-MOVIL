const mongoose = require('mongoose');

const usuarioEsquema = new mongoose.Schema({
    nombre: { type: String, required: true },
    pass: { type: String }
});

module.exports = mongoose.model('Usuario', usuarioEsquema);