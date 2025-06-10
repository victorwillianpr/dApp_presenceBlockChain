// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Presenca {
    address public professor;
    uint public aulaAtual = 1;

    // aula => aluno => presente
    mapping(uint => mapping(address => bool)) public presencas;

    // aula => total de presentes
    mapping(uint => uint) public totalPresencas;

    event PresencaRegistrada(address aluno, uint aula);
    event NovaAula(uint novaAula);

    constructor() {
        professor = msg.sender;
    }

    modifier apenasProfessor() {
        require(msg.sender == professor, "Apenas o professor pode fazer isso");
        _;
    }

    function iniciarNovaAula() public apenasProfessor {
        aulaAtual += 1;
        emit NovaAula(aulaAtual);
    }

    function registrarPresenca() public {
        require(!presencas[aulaAtual][msg.sender], "Presenca ja registrada");

        presencas[aulaAtual][msg.sender] = true;
        totalPresencas[aulaAtual] += 1;

        emit PresencaRegistrada(msg.sender, aulaAtual);
    }

    function verificarPresenca(address aluno, uint aula) public view returns (bool) {
        return presencas[aula][aluno];
    }

    function obterTotalPresentes(uint aula) public view returns (uint) {
        return totalPresencas[aula];
    }
}
