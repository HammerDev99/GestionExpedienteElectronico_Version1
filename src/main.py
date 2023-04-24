from controllers import main_controller

def main():
    """ Clase principal 
    
    Se encarga de inicializar la aplicación aplicando el patrón de diseño Factory Method

    Attributes:
        model: Main_model
        view: Main_view
        controller: Main_controller
        factory: Factory_method
        concrete_factory: Concrete_factory
    """

    """ # Creamos una instancia del Factory Method
    factory = Concrete_factory()

    # Creamos una instancia del Modelo
    model = factory.create_model()
    # Creamos una instancia de la Vista
    view = View()

    # Creamos una instancia del Controlador
    controller = Controller(model, view)
    
    # Agregamos datos al modelo
    controller.add_data("Dato 1")
    controller.add_data("Dato 2")

    # Obtenemos los datos y los mostramos en la vista
    controller.get_data() """
    
    obj = main_controller() 
    obj.__init__()

# Punto de entrada
if __name__ == '__main__':
    main
