<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $nome = $_POST["nome"];
    $matricula = $_POST["matricula"];
    $curso = $_POST["curso"];
    $email = $_POST["email"];
    $curriculo = $_POST["curriculo"];

    // Validar a URL do currículo
    if (filter_var($curriculo, FILTER_VALIDATE_URL)) {
        // URL é válida, processar os dados (neste exemplo, apenas armazená-los em um arquivo de texto)
        $dados = "Nome: $nome\nMatrícula: $matricula\nCurso: $curso\nE-mail: $email\nCurrículo: $curriculo\n\n";
        file_put_contents("membros.txt", $dados, FILE_APPEND);

        // Redirecionar para a página de confirmação
        header("Location: confirmacao.html");
        exit();
    } else {
        // URL inválida, redirecionar de volta ao formulário com uma mensagem de erro
        header("Location: forms.html?erro=url");
        exit();
    }
}
?>
