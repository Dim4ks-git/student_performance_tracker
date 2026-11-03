module com.agile.studentapp {
    requires javafx.controls;
    requires javafx.fxml;

    requires org.controlsfx.controls;
    requires com.dlsc.formsfx;
    requires net.synedra.validatorfx;

    opens com.agile.studentapp to javafx.fxml;
    exports com.agile.studentapp;
}