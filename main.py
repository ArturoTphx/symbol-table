# Esta lista posee las palabras reservadas
# que se utilizan en este caso
dictionary = ["void", "int", "float", "string", "if", "while", "return"]
# Se tiene en un tipo de "constante"
# un string con la llave global
globalKey = "global"
# Tabla semática donde se almacenará todo
table = {hash(globalKey): {}}
# Lista donde se inserta en orden
# los scopes que se van ocupando
# Si se está trabajando sobre
# el scope global, esta lista
# se encontrará vacía
# Se utiliza este complemento
# para respetar la jerarquía
lastScope = []
# Lista donde se insertan los errores
errors = []


# Esta función revise el archivo que se desea
# examinar en una variable llamada source
def read(source):
    cont = 1  # Contador de número de línea
    for line in source:  # Se lee línea por línea
        verifier(line.strip(), cont)  # Se pasa a la función verifier
        # Esta recibe la línea con un strip aplicado
        # y el contador por si se necesita marcar un error
        cont += 1  # Se incrementa el contador


# Esta funcion se encarga de recibir
# una linea de codigo para ser procesada
# de la manera debida
def verifier(line: str, number: int):
    global lastScope
    global globalKey
    # Se verifica si la linea no está completamente vacía
    # en caso contrario se retorna None
    if len(line) != 0:
        if line.count("=") == 1:
            # Se encuentra donde esta
            # el signo de igual y se
            # almacena
            equalIndex = line.find("=")
            # Se pone en una variable
            # lo que hay del índice de igual
            # hacia la izquierda
            left = line[: equalIndex]
            # Se le aplica un strip para mejor
            # manipulacion
            # En este caso hay tres escenarios:
            # Primero:
            # int x = 23
            # left = 'int x'
            # Segundo:
            # x = x + 2
            # left = 'x'
            # Tercero:
            # = 34
            # left = ''
            left = left.strip()
            # Si no hay ningún espacio al separar lo que hay
            # a la izquierda del igual; se procede a velar
            # por un posible caso de asignación a una variable
            # ya creada
            if len(left.split()) == 1:
                # Se verifica si la lista "lastScope" tiene
                # elementos, de lo contrario se hace una búsqueda
                # y manipulación del scope global
                if len(lastScope) == 0:
                    val: dict = table[hash(globalKey)]
                    try:
                        # Se trae la información se la variable
                        # la información es equivalente
                        # al tipo de variable que es
                        info = val[hash(left)]
                        variableProcessing(left, line[equalIndex + 1:].strip(), number, info)
                    except KeyError:
                        # Si no se encontró dicho nombre en el diccionario
                        # global, se procede a marcar un error
                        errors.append(
                            "Error-Línea " + str(
                                number) + " '" + left + "' no está definido")
                # Si se llega a este caso, significa que hay algo en
                # la lista "lastScope", por lo que hay que verificar
                # en orden de jerarquía dónde podría estar el nombre de la
                # variable buscada
                else:
                    scopes = lastScope.copy()
                    scopes.reverse()
                    index = 0
                    while index != len(scopes):
                        val: dict = table[hash(lastScope[index])]
                        try:
                            # Se trae la información se la variable
                            # la información es equivalente
                            # al tipo de variable que es
                            info = val[hash(left)]
                            variableProcessing(left, line[equalIndex + 1:].strip(), number, info)
                            break
                        except KeyError:
                            index = index
                        index = index + 1
                    else:
                        errors.append(
                            "Error-Línea " + str(
                                number) + " '" + left + "' no está definido")
            # De lo contrario se opta por analizar de una vez
            # si es una nueva definición de variable
            else:
                variableProcessing(left, line[equalIndex + 1:].strip(), number)
        # Esta verificación se encarga de analizar si
        # se trata de un if, while u alguna función
        # de otro tipo
        elif line.count("(") == 1 and line.count(")") == 1:
            # Se recolecta la ubicación del primer
            # paréntesis que abre en la línea de código
            fParen = line.find("(")
            # Se recolecta la ubicación del primer
            # paréntesis que cierra en la línea de código
            lParen = line.find(")")
            # Se verifica que la ubicación del primer
            # paréntesis esté antes que el segundo
            # de lo contrario es un error
            if fParen < lParen:
                # Se obtiene lo que está a la izquierda
                # del primer paréntesis para observar
                # cómo se puede clasificar
                left = line[:fParen]
                # Se le aplica un strip para
                # mejor manipulación
                left = left.strip()
                # Se obtiene lo que está entre los paréntesis
                # para analizarlo de manera correcta
                between = line[fParen + 1: lParen]
                # Se le aplica un strip para
                # mejor manipulación
                between = between.strip()
                # Se obtiene lo que está a la derecha del
                # último paréntesis para observar lo que hay
                right = line[lParen + 1:]
                # Se le aplica un strip para
                # mejor manipulación
                right = right.strip()
                # Se verifica si hay únicamente una palabra a la
                # izquierda, en este caso se puede tratar de un
                # if o while
                if len(left.split()) == 1:
                    # Se verifica si se trata de un
                    # if
                    if left == dictionary[4]:
                        conditionProcessing(left, between, right, number)
                    # Se verifica si se trata de un
                    # while
                    elif left == dictionary[5]:
                        conditionProcessing(left, between, right, number)
                    # Se marca error
                    else:
                        errors.append(
                            "Error-Línea " + str(
                                number) + " No se comprende '" + left + "'")
                # Si hay un espacio (se divide
                # en más la parte izquierda); se podría
                # tratar de la definición de una función
                else:
                    # Se verifica que lastScope esté
                    # vacío, ya que esa es la única posibilidad
                    # para definir una función
                    if len(lastScope) >= 1:
                        errors.append(
                            "Error-Línea " + str(
                                number) + " No se puede definir una función en otra")
                        return
                    # Dividimos lo que tenemos a la izquierda
                    # del primer paréntesis para así
                    # manipularlo mejor
                    leftWords = left.split()
                    # Se verifica si se trata de una
                    # definición de función tipo
                    # void
                    if leftWords[0] == dictionary[0]:
                        functionProcessing(leftWords[0], leftWords[1], between, right, number)
                    # Se verifica si se trata de una
                    # definición de función tipo
                    # int
                    elif leftWords[0] == dictionary[1]:
                        functionProcessing(leftWords[0], leftWords[1], between, right, number)
                    # Se verifica si se trata de una
                    # definición de función tipo
                    # float
                    elif leftWords[0] == dictionary[2]:
                        functionProcessing(leftWords[0], leftWords[1], between, right, number)
                    # Se verifica si se trata de una
                    # definición de función tipo
                    # string
                    elif leftWords[0] == dictionary[3]:
                        functionProcessing(leftWords[0], leftWords[1], between, right, number)
                    else:
                        errors.append(
                            "Error-Línea " + str(
                                number) + " No se comprende '" + leftWords[0] + "'")
            else:
                errors.append(
                    "Error-Línea " + str(
                        number) + " Se está haciendo mal uso de los paréntesis")
        # Si hay un cierre de llaves, entonces se tiene
        # que cerrar el último scope
        elif line.count("}") and len(line.split()) == 1:
            # Se verifica que la lista
            # de últimos scopes no esté vacía
            # de lo contrario hay un error
            if len(lastScope) >= 1:
                # Se verifica si el scope coincide con algo global
                if str(lastScope[-1]).find(globalKey) != -1:
                    if len(lastScope) == 2:
                        del lastScope[-1]
                        del lastScope[-1]
                    else:
                        del lastScope[-1]
                else:
                    del lastScope[-1]
            else:
                errors.append(
                    "Error-Línea " + str(
                        number) + " Uso de llaves incorrecto")
        # Se verifica si en la línea se encuentra
        # la palabra reservada return
        elif line.find(dictionary[-1]) != -1:
            # Primero se verifica si se tienen scopes
            # almacenados, en caso contrario
            # se marca error
            if len(lastScope) >= 1:
                # Se verifica si los scopes
                # almacenados coinciden
                # con un scope global, de
                # coincidir se marca error
                if str(lastScope[-1]).find(globalKey) != -1:
                    errors.append(
                        "Error-Línea " + str(
                            number) + " 'return' en posición inválida")
                else:
                    # Si se llega a este punto se tiene
                    # que verificar que se esté empleando
                    # correctamente el return
                    # Primero se divide la línea
                    words = line.split()
                    # Se verifica que la primera (o única)
                    # palabra de la línea sea un return
                    # nuevamente
                    # Así velamos porque no esté en orden
                    # invertido o sea un return sucio
                    if words[0] == dictionary[-1]:
                        # Finalmente verificamos
                        # la longitud por última vez
                        # para fraccionar los casos
                        if len(words) == 1:
                            validReturn("void", number)
                        else:
                            # Se extrae el índice con el primer
                            # espacio (el que sigue después
                            # del return
                            spaceDivider = line.find(" ")
                            validReturn(line[spaceDivider + 1:], number)
                    else:
                        errors.append(
                            "Error-Línea " + str(
                                number) + " No se comprende '" + line + "'")
            else:
                errors.append(
                    "Error-Línea " + str(
                        number) + " 'return' en posición inválida")
        # El resto de escenarios que caigan aquí
        # no están contemplados para ser manejados
        # así que se marca un error
        else:
            errors.append(
                "Error-Línea " + str(
                    number) + " '" + line + "' no se comprende")
    else:
        return


# Esta función se encarga de verificar
# si un nombre está disponible para alguna variable
def validName(name: str):
    # Se verifica que el nombre no sea
    # numérico ni tampoco que se utilice
    # una palabra reservada
    if not name.isnumeric() and name not in dictionary:
        # Se realiza otra verificación para observar que el nombre
        # no posea caracteres inválidos
        if name.find('\"') == -1 and name.find('\"') == -1 \
                and name.find(".") == -1 and name.count("+") == 0 \
                and name.count("-") == 0 and name.count("*") == 0 and name.count("/") == 0 \
                and name.find("(") == -1 and name.find(")") == -1 and name.find("{") == -1 \
                and name.find("}") == -1 and name.find(" ") == -1 and name.find(",") == -1:
            # Se verifica si la lista "lastScope" tiene
            # elementos, de lo contrario se hace una búsqueda
            # global
            if len(lastScope) == 0:
                val: dict = table[hash(globalKey)]
                try:
                    # Se verifica si hay alguna llave
                    # de la tabla que tenga el mismo
                    # hash; de ser cierto esto se retorna
                    # False
                    test = val[hash(name)]
                    return False
                except KeyError:
                    # Si no se encontró dicho nombre en el diccionario
                    # global, se procede a marcar un error
                    return True
            # Si se llega a este caso, significa que hay algo en
            # la lista "lastScope", por lo que hay que verificar
            # en orden de jerarquía dónde podría estar el nombre
            else:
                scopes = lastScope.copy()
                scopes.reverse()
                index = 0
                while index != len(scopes):
                    val: dict = table[hash(lastScope[index])]
                    try:
                        # Se verifica si hay alguna llave
                        # de la tabla que tenga el mismo
                        # hash; de ser cierto esto se retorna
                        # False
                        test = val[hash(name)]
                        return False
                    except KeyError:
                        index = index
                    index = index + 1
                else:
                    return True
        else:
            return False
    else:
        return False


# Procesa la definición de variable o reasignación de valores
# a una variable
def variableProcessing(left: str, right: str, number: int, var: str = "empty"):
    # Se verifica si la variable que
    # viene por parámetro está en un
    # valor igual a "empty". En caso
    # de ser cierto se trata de una nueva
    # asignación, de lo contrario
    # hay que velar por una composición
    # únicamente
    if var == "empty":
        # Se le aplica un split a left
        # (lo que está a la izquierda del igual)
        # Ejemplo:
        # int x = ...
        # Con el split quedaría: 'int', 'x'
        leftWords = left.split()
        # Ahora se verifica si el tamaño de
        # leftWords está permitido
        # En caso contrario marca error
        if len(leftWords) == 2:
            # Si el nombre que se le quiere poner a la variable
            # no es numérico y tampoco está en el diccionario;
            # entonces se procede a continar.
            # En caso contrario se marca error
            if validName(leftWords[1]):
                # Si el tipo de lo que se quiere declarar
                # es int o float
                if leftWords[0] == dictionary[1] or leftWords[0] == dictionary[2]:
                    numericProcessing(leftWords[1], right, leftWords[0], number)
                # Si el tipo de lo que se quiere declarar
                # es string
                elif leftWords[0] == dictionary[3]:
                    stringProcessing(leftWords[1], right, leftWords[0], number)
                else:
                    errors.append(
                        "Error-Línea " + str(
                            number) + " '" + leftWords[0] + "' no se comprende")
            else:
                errors.append(
                    "Error-Línea " + str(
                        number) + " '" + leftWords[1] + "' No es un nombre valido")
        else:
            errors.append(
                "Error-Línea " + str(
                    number) + " '" + left + "' no se comprende")
    else:
        # Si el tipo de lo que se quiere declarar
        # es int o float
        if var == dictionary[1] or var == dictionary[2]:
            numericProcessing(left, right, var, number)
        # Si el tipo de lo que se quiere declarar
        # es string
        elif var == dictionary[3]:
            stringProcessing(left, right, var, number)
        else:
            errors.append(
                "Error-Línea " + str(
                    number) + " '" + left + "' no se comprende")


# Función encargada de velar por la
# concordancia en una composición de
# variable numérica
# Ej:
# int x = 3
# Verifica si 3 está bien para componer
# a un valor int o float
# Además si se tiene:
# float x = 43.0
# float z = x + 5.0
# Verificando "z", corrobora si
# x y 5.0 es correcto para un valor tipo int
# o float
# Se toma igual para int o float, ya que en C++
# se permite de esta manera
def numericProcessing(name: str, composition: str, var: str, number: int):
    const = 10000000
    pause = 0
    while pause != -1:
        indexPlus = composition.find("+")  # Indíce del primer signo de suma
        if indexPlus == -1:
            indexPlus = const

        indexSubs = composition.find("-")  # Indíce del primer signo de resta
        if indexSubs == -1:
            indexSubs = const

        indexProfs = composition.find("*")  # Indíce del primer signo de multiplicación
        if indexProfs == -1:
            indexProfs = const

        indexDiv = composition.find("/")  # Indíce del primer signo de división
        if indexDiv == -1:
            indexDiv = const

        if indexPlus < indexSubs and indexPlus < indexProfs and indexPlus < indexDiv:
            line = composition[: indexPlus]
            line = line.strip()
            composition = composition[indexPlus + 1:]
            search(line, name, var, number)
        elif indexSubs < indexPlus and indexSubs < indexProfs and indexSubs < indexDiv:
            line = composition[: indexSubs]
            line = line.strip()
            composition = composition[indexSubs + 1:]
            search(line, name, var, number)
        elif indexDiv < indexPlus and indexDiv < indexSubs and indexDiv < indexProfs:
            line = composition[: indexDiv]
            line = line.strip()
            composition = composition[indexDiv + 1:]
            search(line, name, var, number)
        elif indexProfs < indexPlus and indexProfs < indexSubs and indexProfs < indexDiv:
            line = composition[: indexProfs]
            line = line.strip()
            composition = composition[indexProfs + 1:]
            search(line, name, var, number)
        elif indexPlus == const and indexSubs == const and indexProfs == const and indexDiv == const:
            composition = composition.strip()
            search(composition, name, var, number)
            insertVariable(name, var)
            break


# Función encargada de velar por la
# concordancia en una composición de
# variable tipo string
# Ej:
# string x = "Arturo"
# Verifica si "Arturo" está bien para componer
# a un valor string
# Además si se tiene:
# string x = "Jorge"
# string z = x + "Arturo"
# Verificando "z", corrobora si
# x y "Arturo" es correcto para un valor tipo string
def stringProcessing(name: str, composition: str, var: str, number: int):
    pause = 0
    while pause != -1:
        indexPlus = composition.find("+")  # Indíce del primer signo de suma

        indexSubs = composition.find("-")  # Indíce del primer signo de resta

        indexProfs = composition.find("*")  # Indíce del primer signo de multiplicación

        indexDiv = composition.find("/")  # Indíce del primer signo de división

        # Si en el intento de composición de un string
        # se detectan restas, multiplicaciones o divisiones;
        # se tendrá que marcar un error
        if indexSubs != -1 or indexProfs != -1 or indexDiv != -1:
            errors.append(
                "Error-Línea " + str(number) + " No se permiten *, / o - en la declaración de un string")
            return
        elif indexPlus != -1:
            line = composition[: indexPlus]
            line = line.strip()
            search(line, name, var, number)
        elif indexPlus == -1:
            composition = composition.strip()
            search(composition, name, var, number)
            insertVariable(name, var)
            pause = -1
            return


# Función encargada de observar si un
# dato que se necesita asignar está
# bien definido o no, es un complemento de la
# función anterior y trasanterior
def search(data: str, name: str, var: str, number: int):
    # Se verifica si la variable en el código
    # es de tipo int o float, así se harán ciertos
    # procedimientos de estos
    if var == dictionary[1] or var == dictionary[2]:
        if isInt(data) or isFloat(data):
            return
        else:
            finalSearch(data, name, var, number)
    # Se verifica si el tipo es string
    elif var == dictionary[3]:
        if isString(data):
            return
        else:
            finalSearch(data, name, var, number)
    else:
        errors.append(
            "Error-Línea " + str(
                number) + " '" + data + "' no está definido")


# Esta función busca en los scopes
# para así poder dar un veredicto final
# sobre el nombre de la variable
# que está intentando componer
# a la nueva
def finalSearch(data: str, name: str, var: str, number: int):
    global lastScope
    # Se hace una copia de la lista
    # lastScope para poder hacer ciertas
    # operaciones más adelante
    scopes = lastScope.copy()
    if len(scopes) == 0:
        val: dict = table[hash(globalKey)]
        try:
            info = val[hash(data)]
            if info == var:
                return
            else:
                errors.append(
                    "Error-Línea " + str(
                        number) + " Asignando '" + data + "' a '" + name + "' Los tipos difieren")
        except KeyError:
            errors.append(
                "Error-Línea " + str(
                    number) + " '" + data + "' no está definido o no concuerda con la definición")
    else:
        scopes.reverse()
        index = 0
        while index != len(scopes):
            val: dict = table[hash(lastScope[index])]
            try:
                info = val[hash(data)]
                if info == var:
                    return
            except KeyError:
                index = index
            index = index + 1
        errors.append(
            "Error-Línea " + str(
                number) + " '" + data + "' no está definido o no concuerda con la definición")


# Método encargado de insertar
# una variable en una tabla
# (en la que se tiene el último
# scope)
def insertVariable(name: str, var: str):
    global lastScope
    if len(lastScope) == 0:
        val: dict = table[hash(globalKey)]
        val[hash(name)] = var
    else:
        val: dict = table[hash(lastScope[-1])]
        val[hash(name)] = var


# Esta función valida lo que posea
# una condición entre sus paréntesis
# Ejemplo:
# 1. if (x > 34) {
# 2.    x = x - 1
# 3. }
# La función recibe:
# left = if between = x > 34 right = { y number = 1
def conditionProcessing(left: str, between: str, right: str, number: int):
    global lastScope
    if between.count(dictionary[0]) >= 1 or between.count(dictionary[1]) >= 1 or between.count(
            dictionary[2]) >= 1 or between.count(dictionary[3]) >= 1 or between.count("=") == 1:
        # Si alguna o todas las condiciones son verdaderas, entonces se
        # procede a marcar error, puesto que en las
        # declaraciones de if o while no es posible
        # tener una declaración de tipo en la línea
        errors.append(
            "Error-Línea " + str(number) + " Definición de condición incorrecta")
    else:
        # Si la verificación anterior falló, entonces se procede
        # a continuar registrando el scope en la tabla con
        # una combinación
        if len(lastScope) == 0:
            table[hash(globalKey + str(number))] = {}
            lastScope.append(globalKey)
            lastScope.append(globalKey + str(number))
        else:
            table[hash(lastScope[0] + str(number))] = {}
            lastScope.append(lastScope[0] + str(number))
        conditionParams(between, number)


# Esta función valida lo que posea
# entre los paréntesis una condición
# Es usada por "conditionProcessing"
# Ejemplo:
# if (x > 34) {
#     x = x - 1
# }
# La función recibe:
# x > 34
def conditionParams(between: str, number: int):
    # Función que verifica los parámetros o valores
    # de una condición if o while
    # recibe lo que está entre paréntesis
    # el número de línea
    # y el tipo de scope
    between = between.strip()
    indexMore = between.find("<")  # Índice donde está
    # el primer < si se encuenta
    indexLess = between.find(">")  # Índice donde está
    # el primer > si se encuenta
    indexEqual = between.find("=")  # Índice donde está
    # el primer = si se encuenta
    if indexMore != -1 and between.count("<") == 1:
        left = between[: indexMore]
        right = between[indexMore + 1:]
        left = left.strip()
        right = right.strip()
        sidesAnalysis(right, left, between[indexMore], number)
    elif indexLess != -1 and between.count(">") == 1:
        left = between[: indexLess]
        right = between[indexLess + 1:]
        left = left.strip()
        right = right.strip()
        sidesAnalysis(right, left, between[indexLess], number)
    elif indexEqual != -1 and between.count("=") == 2 and between[indexEqual + 1] == "=":
        left = between[: indexEqual]
        right = between[indexEqual + 2:]
        left = left.strip()
        right = right.strip()
        sidesAnalysis(right, left, between[indexEqual: indexEqual + 2].strip(), number)
    elif indexMore == -1 and indexEqual == -1 and indexLess == -1:
        errors.append(
            "Error-Línea " + str(number) + " La condición debe tener los signos <, > o ==")


# Esta función valida lo que posea
# la izquierda, derecha y signo de
# una condición
# Es usada por "conditionValidation"
# Ejemplo:
# if (x > 34) {
#     x = x - 1
# }
# La función recibe:
# right = x, left = 34, sign = > y el número de línea
def sidesAnalysis(right: str, left: str, sign: str, number: int):
    global lastScope
    # Se verifica si los lados están
    # vacíos o no
    if len(left) >= 1 and len(right) >= 1:
        # Se verifica que ambos lados
        # no estén fraccionados con
        # espacios, ya que esto
        # es inválido
        if len(left.split()) == 1 and len(right.split()) == 1:
            leftType = "void"
            rightType = "void"
            if isInt(left):
                leftType = "int"
            elif isFloat(left):
                leftType = "float"
            elif isString(left):
                leftType = "string"
            else:
                scopes = lastScope.copy()
                scopes.reverse()
                index = 0
                while index != len(scopes):
                    val: dict = table[hash(lastScope[index])]
                    try:
                        # Se verifica si hay alguna llave
                        # de la tabla que tenga el mismo
                        # hash; que el nombre del dato
                        # que se tiene
                        leftType = val[hash(left)]
                    except KeyError:
                        index = index
                    index = index + 1
            if isInt(right):
                rightType = "int"
            elif isFloat(right):
                rightType = "float"
            elif isString(right):
                rightType = "string"
            else:
                scopes = lastScope.copy()
                scopes.reverse()
                index = 0
                while index != len(scopes):
                    val: dict = table[hash(lastScope[index])]
                    try:
                        # Se verifica si hay alguna llave
                        # de la tabla que tenga el mismo
                        # hash; que el nombre del dato
                        # que se tiene
                        rightType = val[hash(right)]
                    except KeyError:
                        index = index
                    index = index + 1
            if rightType != "void":
                if leftType != "void":
                    typeAgreement(rightType, leftType, number)
                else:
                    errors.append(
                        "Error-Línea " + str(number) + " No se comprende '" + left + "'")
            else:
                errors.append(
                    "Error-Línea " + str(number) + " No se comprende '" + right + "'")
        else:
            errors.append(
                "Error-Línea " + str(number) + " No se comprende '" + left + sign + right + "'")
    else:
        errors.append(
            "Error-Línea " + str(number) + " No se comprende '" + left + sign + right + "'")


# Esta función valida lo que posea
# la correcta sobrecarga del operador asignado
# mediante los tipos previamente clasificados
# de la izquierda y derecha de una condición
# Esta función recibe directamente los tipos
# de ambos sitios
def typeAgreement(rightType: str, leftType: str, number: int):
    if rightType == leftType:
        return
    elif (rightType == "int" and leftType == "float") or (rightType == "float" and leftType == "int"):
        return
    else:
        errors.append(
            "Error-Línea " + str(number) + " No se puede comparar un valor " + leftType + " con " + rightType)


# Esta función es utilizada por
# functionProcessing y se encarga
# de velar porque no haya impuresas
# en lo que venga entre paréntesis
def validBetween(between: str):
    if between.find(".") == -1 and between.count("+") == 0 \
            and between.find('\"') == -1 and between.find('\"') == -1 \
            and between.count("-") == 0 and between.count("*") == 0 and between.count("/") == 0 \
            and between.find("(") == -1 and between.find(")") == -1 and between.find("{") == -1 \
            and between.find("}") == -1:
        return True
    else:
        return False


# Esta función se encarga de verificar
# si la definición de una función
# es correcta
# Ej:
# 3. void swap(int x, int y) {
# La función recibe
# var = void, name = swap, between = int x, int y, left = { y number = 3
def functionProcessing(var: str, name: str, between: str, left: str, number: int):
    global lastScope
    # Primero se verifica si el nombre es válido con
    # la función validName
    if validName(name):
        # Seguidamente se procede a observar que
        # no se tengan impuresas en las variables
        # que vienen entre paréntesis
        if validBetween(between):
            # Ahora se procede a registrar
            # la función dentro del scope
            # global
            val: dict = table[hash(globalKey)]
            # Se registra el tipo de la
            # función
            val[hash(name)] = var
            # Ahora se crea un diccionario
            # con el nombre de la función
            # para añadir en este sus
            # parémetros y variables
            table[hash(name)] = {}
            # Se añade a la lista
            # lastScope el nombre de
            # la nueva función
            lastScope.append(name)
            # Seguidamente se procede a verificar
            # si hay algo adentro del string
            # between, ya que si es una función
            # sin parámetros, se procede a
            # retornar
            if len(between) == 0:
                return
            else:
                # Si hay algo adentro de
                # between procedemos a
                # verificar
                paramsVerification(between, number)
        else:
            errors.append(
                "Error-Línea " + str(number) + " La función " + name + " tiene una definición incorrecta")
    else:
        errors.append(
            "Error-Línea " + str(number) + " El nombre " + name + " con es inválido")


# Función encargada de
# observar los parámetros de una función
# y verificarlos
# Ejemplo:
# 8. void swap(int x, int y) {
#      int tmp = x
#      x = y
#      y = tmp
# }
# Esta función recibe:
# between = int x, int y, swap y number = 8
# Esta función se usa por
# la de arriba
def paramsVerification(between: str, number: int):
    pause = 0
    while pause != -1:
        # Verifica si la cadena entrante tiene comas
        # Ya que si no posee, se procede a realizar otro movimiento
        if between.count(",") >= 1:
            # Se extrae el índice donde se encuentra la primera coma
            # para manipular esa declaración de parámetro
            divider = between.find(",")
            # Se recolecta donde se debe
            # encontrar el primer parámetro de between
            param = between[:divider]
            # Se aplica un strip para manipulación correcta manipulación
            param = param.strip()
            # Se procede a llamar a la verificación
            # individual del posible parámetro
            paramValidation(param, number)
            # Se actualiza between para poder continuar con el
            # ciclo de manera correcta
            between = between[divider + 1:]
        else:
            # Se aplica un strip para una manipulación correcta
            # a lo que queda en between
            between = between.strip()
            # Se procede a llamar a la verificación
            # individual del posible parámetro
            paramValidation(between, number)
            pause = -1
            return


# Función encargada de observar cada parámetro
# individualmente y agregarlo
# al diccionario de la función
# Ej:
# string b
# Verifica que "string b" esté bien planteado
def paramValidation(param: str, number: int):
    global lastScope
    # Dividimos la declaración del parámetro
    words = param.split()
    # Se verifica que el parémetro
    # la variable words únicamente
    # contenga dos cosas
    # De tener más es un error
    if len(words) == 2:
        # Se verifica que el nombre del parámetro no sea
        # sea correcto verificando que no tenga nada
        # numérico, puesto que ya hubo una verificación
        # previa
        if not words[1].isnumeric():
            # Se verifica que el parámetro
            # sea de un tipo aceptado
            if words[0] == "string" or words[0] == "int" or words[0] == "float":
                # Finalmente se agrega a la tabla
                # en el último diccionario
                # del scope registrado
                val: dict = table[hash(lastScope[-1])]
                # Se registra con su respectivo
                # nombre y tipo
                val[hash(words[1])] = words[0]
            else:
                errors.append(
                    "Error-Línea " + str(number) + " Se desconoce la definición de '" + words[0] + "'")
        else:
            errors.append(
                "Error-Línea " + str(number) + " No se puede declarar el nombre de una variable como '" +
                words[1] + "'")
    else:
        errors.append(
            "Error-Línea " + str(number) + " No se puede comprender la sintaxis del parámetro '" + words[0] + "'")


# Esta función se encarga de verificar
# si un return coincide con el scope
# de la función utilizada
# Ej:
# 7. string world(){
# 8.    return "Hola"
# 9. }
# La función recibe:
# right = "Hola" y number = 8
# Además verifica si right contiene un valor de retorno
# válido
def validReturn(right: str, number: int):
    global globalKey
    global lastScope
    # Se saca el diccionario global
    # de la tabla, ya que aquí se almacenó
    # el tipo de variable de la función
    val: dict = table[hash(globalKey)]
    # Después se tiene que observar la primera
    # posición en la lista lastScope ya que
    # en esta se encuentra el nombre del último scope
    # agregado
    # Se guarda en info el tipo de variable de
    # la función
    info = val[hash(lastScope[0])]
    # Ahora se procede a verificar según
    # este tipo
    # Primero se hace para el tipo void
    if info == dictionary[0]:
        # Si el lado derecho
        # viene igual a void
        # significa que en el reconocimiento
        # no se encontró nada a la derecha
        # del return
        # Por ende se retorna
        # En caso contrario se marca
        # un error
        if right == "void":
            return
        else:
            errors.append(
                "Error-Línea " + str(number) + " Función void únicamente puede devolver vacío")
    # Se verifica si el tipo de función es int
    # con sus respectivos casos
    elif info == dictionary[1]:
        # Si se intenta hacer un return
        # de algo que calza con un valor
        # entero, se procede a hacer return
        # En caso contrario se tiene que procesar
        # una búsqueda
        if isInt(right):
            return
        else:
            returnSearch(right, info, number)
    # Se verifica si el tipo de función es float
    # con sus respectivos casos
    elif info == dictionary[2]:
        # Si se intenta hacer un return
        # de algo que calza con un valor
        # flotante, se procede a hacer return
        # En caso contrario se tiene que procesar
        # una búsqueda
        if isFloat(right):
            return
        else:
            returnSearch(right, info, number)
    # Se verifica si el tipo de función es float
    # con sus respectivos casos
    elif info == dictionary[3]:
        # Si se intenta hacer un return
        # de algo que calza con un valor
        # string, se procede a hacer return
        # En caso contrario se tiene que procesar
        # una búsqueda
        if isString(right):
            return
        else:
            returnSearch(right, info, number)


# Esta función se encarga de buscar
# un posible nombre de alguna variable
# para poder verificar su tipo con el que
# se le manda por parámetro
# Así se hace una decisión final
def returnSearch(right: str, info: str, number: int):
    global lastScope
    scopes = lastScope.copy()
    scopes.reverse()
    index = 0
    while index != len(scopes):
        val: dict = table[hash(lastScope[index])]
        try:
            # Se accede al tipo
            # guardado del posible nombre
            # de la variable
            var = val[hash(right)]
            if var == info:
                return
            else:
                errors.append(
                    "Error-Línea " + str(number) + " Valor de retorno no coincide")
            return
        except KeyError:
            index = index
        index = index + 1
    else:
        errors.append(
            "Error-Línea " + str(number) + " '" + right + "' no está definido o no coincide con el valor de retorno")


# Función booleana simple que se encarga de
# discriminar si el string recibido es
# un float
def isFloat(var: str):
    if len(var.split()) == 1:
        if var.isnumeric():
            return True
        elif var.count(".") == 1:
            pointDivider = var.find(".")
            # En este caso se maneja el uso de únicamente un punto
            # ya que dos no son permitidos
            left = var[: pointDivider]  # Se almacena lo que está a la izquierda del punto
            right = var[pointDivider + 1:]  # Se almacena lo que está a la derecha del punto
            if left.isnumeric() and right.isnumeric():
                return True
            else:
                return False
        else:
            return False
    else:
        return False


# Función booleana simple que se encarga de
# discriminar si el string recibido es
# un string
def isString(var: str):
    if var.count('\"') == 2 and var[0] == '\"' and var[-1] == '\"':
        # Si la variable tiene las condiciones para ser
        # un string se retorna verdadero
        return True
    else:
        return False


# Función booleana simple que se encarga de
# discriminar si el string recibido es
# un int
def isInt(var: str):
    if len(var.split()) == 1:
        if var.isnumeric():
            # Si la variable tiene las condiciones para ser
            # un int se retorna verdadero
            return True
        else:
            return False
    else:
        return False


if __name__ == '__main__':
    file = open('code.txt', 'r')
    read(file)
    if len(errors) == 0:
        print("No hay errores en el código")
    else:
        for error in errors:
            print(error)
    file.close()
