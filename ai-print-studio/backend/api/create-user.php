
<?php
$servername = "localhost";
$username = "root";
$password = "";
$db = "fixdis";

try {
    $conn = new PDO("mysql:host=".$servername.";dbname=".$db.";charset=utf8", $username, $password);
    // set the PDO error mode to exception
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    // echo "Connected successfully";
} catch(PDOException $e) {
    echo "Connection failed: " . $e->getMessage();
    die();
}
?>
<?php
    session_start(); // Iniciar la sesión 

    if (!isset($_SESSION["id_usuario"])) {
        header("location: login.php");
    }

    $idEmpresa = $_SESSION["id_empresa"];
    $id_usuario = $_SESSION["id_usuario"];
    $tipo_usuario = $_SESSION["tipo_usuario"];

    require "conexion.php";
    require "permisos.php";

$selectTipoDocUsuario="";
$nro=null;
$nombre=null;
$apellido=null;
$mail=null;
$mostrarAlert = false; // Variable para controlar la visualización del alert
$error =0;
// Aquí procesamos los datos del formulario ANTES de que se genere cualquier HTML
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Procesar los datos del formulario
    $selectTipoDeUsuario = htmlspecialchars($_POST["selectTipoDeUsuario"]);
    $selectTipoDeUsuario = strtoupper(trim($selectTipoDeUsuario)); //Lo paso a mayúsculas    
    $selectTipoDocUsuario = htmlspecialchars($_POST["selectTipoDocUsuario"]);
    $selectTipoDocUsuario = strtoupper(trim($selectTipoDocUsuario)); //Lo paso a mayúsculas    
    $nro = $_POST["nro"];
    //Para insertar por default la primera password como el numero de documento
    $clave = $_POST["nro"];
    $nombre = htmlspecialchars($_POST["nombre"]);
    $nombre = strtoupper(trim($nombre)); //Lo paso a mayúsculas
    $apellido= htmlspecialchars($_POST["apellido"]);
    $apellido = strtoupper(trim($apellido)); //Lo paso a mayúsculas
    $mail= htmlspecialchars($_POST["mail"]);
    $mail = strtoupper(trim($mail)); //Lo paso a mayúsculas

    if(!empty($selectTipoDocUsuario) && !empty($nro) && !empty($nombre) && !empty($apellido) && !empty($mail) ){
        try {      
            $query = "INSERT INTO USUARIOS (tipo_usuario,id_empresa, tipo_documento, numero_documento, nombre, apellido, email,clave) 
                      VALUES (:selectTipoDeUsuario, :empresa, :selectTipoDocUsuario, :nro, :nombre, :apellido, :email, :clave)";
            $resultadoQuery = $conn->prepare($query);
            $resultadoQuery->bindParam(':empresa', $idEmpresa);
            $resultadoQuery->bindParam(':selectTipoDeUsuario', $selectTipoDeUsuario);
            $resultadoQuery->bindParam(':selectTipoDocUsuario', $selectTipoDocUsuario);
            $resultadoQuery->bindParam(':nro', $nro);
            $resultadoQuery->bindParam(':nombre', $nombre);
            $resultadoQuery->bindParam(':apellido', $apellido);
            $resultadoQuery->bindParam(':email', $mail);
            $resultadoQuery->bindParam(':clave', $clave);
            $resultadoQuery->execute();
            
            // Activar el alert
            $mostrarAlert = true; // Cambiar a true para mostrar el alert
        } catch (PDOException $e) {
            // Manejar cualquier error en la inserción
            $query = "SELECT numero_documento
            FROM USUARIOS
            WHERE numero_documento =:nro 
            AND id_empresa= :id_empresa";
            $respuestaQuery = $conn->prepare($query);
            $respuestaQuery->bindParam(':nro', $nro);
            $respuestaQuery->bindParam(':id_empresa', $idEmpresa);
            $respuestaQuery->execute();          
            $Usuario = $respuestaQuery->fetch(PDO::FETCH_ASSOC);
        
            //Si no hay resultados, devolver un array vacío
            if ($Usuario) {
                // $error ="No se puede crear el usuario porque ya existe.";
                $error = 1;
            } else {
                // $error ="Error al insertar el usuario.";
                $error = 2;
            }
        }
    }        
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.5.0/font/bootstrap-icons.css">    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
    <script src="./JS/script-creo-Usuario.js" defer></script>
    <link rel="stylesheet" href="./CSS/style-contenido-general.css">    
    <title>Crear Usuario</title>
</head>
<body>
    <div class="contenedor">
        <div class="row form-Registro">
        <?php if(!Permisos::tienePermiso('abm_usuario', $id_usuario)){?>
                    <div class="alert alert-danger text-center mt-4" role="alert">
                        Usted no tiene permiso a esta acción!
                    </div>
                    <?php
                    echo "<script>
                                setTimeout(function(){
                                window.location.href = 'logout.php';
                                }, 4000); 
                        </script>";
                    die();    
                }
        ?>
        <?php
            require "menuGeneral.php";
        ?>           
            <div class="col-12 col-sm-10 offset-sm-2 col-md-10 offset-md-2 col-lg-9 offset-lg-2" id="opciones">
                <form method="POST" action="" id="registroUsuario">
                <div class="row justify-content-center"> 
                    <div class="col-12 col-sm-10 col-md-8 col-lg-5 mb-2" id="personal">
                        <?php if($error !=0){?>                        
                        <div class="alert alert-danger alert-dismissible fade show" role="alert">
                            <?php if($error == 1){?>
                                <strong>Error!</strong> el usuario ya existe en el sistema.
                            <?php }else{?>
                                <strong>Error!</strong> no se puedo registrar usuario.
                            <?php }?>
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                        </div>
                        <?php } ?>
                            <div class="datosPersonales"> 
                                <p class="display-6 text-center" id="">
                                    <img src="./img/agregarUser.png">   
                                    Datos Personales
                                </p>       
                                <select class="form-select mb-3" id="selectTipoDeUsuario" name="selectTipoDeUsuario">
                                    <option selected disabled value="0">Tipo de Usuario</option>
                                    <option value="EMPLEADO">Operador</option>       
                                    <option value="CLIENTE">Cliente</option>                                      
                                </select>                                   
                                <small class="text-danger d-none" id="smTipoUsuario">Debe seleccionar un tipo de Usuario</small>  
                                <select class="form-select mb-3" id="selectTipoDocUsuario" name="selectTipoDocUsuario">
                                    <option selected disabled value="0">Tipo de Documento</option>
                                    <option value="dni">DNI</option>
                                </select>                                  
                                <small class="text-danger d-none" id="smTipoDoc">Debe seleccionar un tipo de Documento</small>  
                                <div class="input-group mb-3">
                                    <span class="input-group-text">Nro Documento:</span>
                                    <input type="text" class="form-control" placeholder="Numero de documento" id="nro" name="nro" minlength="8" required>                                    
                                </div>                                                                         
                                <small class="text-danger d-none" id="smNroDoc">Debe definir un numero de documento valido</small>  
                                <div class="input-group mb-3">
                                    <span class="input-group-text">Nombre</span>
                                    <input type="text" class="form-control" placeholder="Nombre" name="nombre" id="nombre" minlength="2" required>
                                </div>
                                <small class="text-danger d-none" id="smNombre">Debe definir un nombre valido</small>  
                                <div class="input-group mb-3">
                                    <span class="input-group-text">Apellido</span>
                                    <input type="text" class="form-control" placeholder="Apellido" name="apellido" id="apellido" minlength="2" required>
                                </div>                                
                                <small class="text-danger d-none" id="smApellido">Debe definir un apellido valido</small>  
                                <div class="input-group mb-3">
                                    <span class="input-group-text">@Mail</span>
                                    <input type="text" class="form-control" placeholder="Mail" name="mail" id="mail" minlength="10" maxlength="50" required>
                                </div>
                                <small class="text-danger d-none" id="smMail">Debe definir un mail valido</small>  
                                <div class="mb-3 border">
                                    <a href="./indexAdminEmpresa.php" class="btn btn-primary" type="submit">Volver</a> 
                                    <button class="btn btn-primary" type="submit">Guardar</button>  
                                </div>                        
                            </div>
                        </div>              
                    </div>                         
                </form>
            </div>
        </div>
    </div>    
</body>
</html>
