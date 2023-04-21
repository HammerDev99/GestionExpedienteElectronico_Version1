from controllers import main_controller

def main():
    """ # Creamos una instancia del Factory Method
    factory = ConcreteFactory()

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
