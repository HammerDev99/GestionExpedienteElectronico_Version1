from controllers import main_controller
from models import main_model
from views import main_view

def main():
    """
    Se encarga de inicializar la aplicación aplicando el patrón de diseño Factory Method

    Attributes:
        model: Main_model
        view: Main_view
        controller: Main_controller
    """

    view = main_view.MainView()
    model = main_model.MainModel()
    controller = main_controller.MainController(model, view)
    controller.run()

    """ 
    #Código a implementar si se usa el pratrón de diseño Factory Method

    # Creamos una instancia del Factory Method
    factory = ConcreteFactory()

    # Creamos una instancia del Modelo
    model = factory.create_model()
    # Creamos una instancia de la Vista
    view = View()

    # Creamos una instancia del Controlador
    controller = Controller(model, view)

    # Obtenemos los datos y los mostramos en la vista
    controller.get_data() 
    """

# Punto de entrada
if __name__ == '__main__':
    main()
    