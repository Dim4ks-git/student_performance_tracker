module ie.mtu.studenttracker {
    requires javafx.controls;
    requires javafx.fxml;

    opens ie.mtu.studenttracker to javafx.fxml;
    exports ie.mtu.studenttracker;
}
