const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const { ApolloServer, gql } = require('apollo-server-express');
const Usuario = require('./models/usuario');

mongoose.connect('mongodb://localhost:27017/pr5');

const typeDefs = gql`
    type Usuario {
        id: ID!
        nombre: String
        pass: String
    }
    input UsuarioInput {
        nombre: String
        pass: String
    }
    type Alert {
        message: String
    }
    type Query {
        getUsuarios: [Usuario]
        getUsuariosById(id: ID!): Usuario
    }
    type Mutation {
        addUsuario(input: UsuarioInput): Usuario
        updateUsuario(id: ID!, input: UsuarioInput): Usuario
        delUsuario(id: ID!): Alert
    }
`;

const resolvers = {
    Query: {
        getUsuarios: async () => {
            return await Usuario.find();
        },
        getUsuariosById: async (obj, { id }) => {
            const usuarioBus = await Usuario.findById(id);
            if (!usuarioBus) return null;
            return usuarioBus;
        }
    },
    Mutation: {
        addUsuario: async (obj, { input }) => {
            const usuario = new Usuario(input);
            await usuario.save();
            return usuario;
        },
        updateUsuario: async (obj, { id, input }) => {
            const usuario = await Usuario.findByIdAndUpdate(id, input, { new: true });
            return usuario;
        },
        delUsuario: async (obj, { id }) => {
            await Usuario.deleteOne({ _id: id });
            return { message: "Usuario eliminado" };
        }
    }
};

async function iniciarServidor() {
    const app = express();
    app.use(cors());

    const server = new ApolloServer({ typeDefs, resolvers });
    await server.start();
    server.applyMiddleware({ app });

    app.listen(8090, () => {
        console.log(`Servidor GraphQL pr5 http://localhost:8090${server.graphqlPath}`);
    });
}

iniciarServidor();