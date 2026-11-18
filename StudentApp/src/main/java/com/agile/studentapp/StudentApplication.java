package com.agile.studentapp;

import javafx.application.Application;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.geometry.Insets;
import javafx.scene.control.ComboBox;
import javafx.scene.control.Label;
import javafx.scene.control.Spinner;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.TextField;
import javafx.scene.layout.GridPane;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
import javafx.scene.text.Text;
import javafx.stage.Stage;

import java.io.IOException;

public class StudentApplication extends Application {
    @Override
    public void start(Stage primaryStage) throws IOException {
        primaryStage.setTitle("Student Form");

        // Creating GridPane
        GridPane grid = new GridPane();
        grid.setAlignment(Pos.CENTER);
        grid.setHgap(10);
        grid.setVgap(10);
        grid.setPadding(new Insets(25, 25, 25, 25));

        // Creating/Setting Scene
        Scene scene = new Scene(grid, 960, 720);
        primaryStage.setScene(scene);


        Text sceneTitle = new Text("Student Form");
        sceneTitle.setFont(Font.font("Tahoma", FontWeight.NORMAL, 20));
        grid.add(sceneTitle, 0, 0, 2, 1);

        Label q1 = new Label("How old are you?");
        grid.add(q1, 0, 1);

        Spinner q1box = new Spinner(14, 21, 16);
        q1box.setEditable(true);
        grid.add(q1box, 1, 1);

        Label q2 = new Label("What gender do you identify as?");
        grid.add(q2, 0, 2);

        ObservableList<String> q2options =
                FXCollections.observableArrayList(
                        "Male",
                        "Female",
                        "Other"
                );
        final ComboBox q2box = new ComboBox(q2options);
        grid.add(q2box, 1, 2);

        Label q3 = new Label("What type of School did you attend?");
        grid.add(q3, 0, 3);

        ObservableList<String> q3options =
                FXCollections.observableArrayList(
                        "Public",
                        "Private",
                        "Charter"
                );
        final ComboBox q3box = new ComboBox(q3options);
        grid.add(q3box, 1, 3);

        Label q4 = new Label("How would you describe your family's income?");
        grid.add(q4, 0, 4);

        ObservableList<String> q4options =
                FXCollections.observableArrayList(
                        "Low",
                        "Lower-Middle",
                        "Middle",
                        "Upper-Middle",
                        "Upper"
                );
        final ComboBox q4box = new ComboBox(q4options);
        grid.add(q4box, 1, 4);

        Label q5 = new Label("What level of education did your parents have? (Highest Applicable)");
        grid.add(q5, 0, 5);

        ObservableList<String> q5options =
                FXCollections.observableArrayList(
                        "Doctorate",
                        "Masters",
                        "Bachelors",
                        "Associate",
                        "High School",
                        "(None Apply)"
                );
        final ComboBox q5box = new ComboBox(q5options);
        grid.add(q5box, 1, 5);

        Label q6 = new Label("How many hours a day do you study?");
        grid.add(q6, 0, 6);

        Spinner q6box = new Spinner(0, 24, 0);
        q6box.setEditable(true);
        grid.add(q6box, 1, 6);

        Label q7 = new Label("What score did you receive on your previous exam?");
        grid.add(q7, 0, 7);

        Spinner q7box = new Spinner(0, 100, 50);
        q7box.setEditable(true);
        grid.add(q7box, 1, 7);

        Label q8 = new Label("What kind of notes do you keep?");
        grid.add(q8, 0, 8);

        ObservableList<String> q8options =
                FXCollections.observableArrayList(
                        "Great notes",
                        "Good notes",
                        "Occasional notes",
                        "Sporadic notes",
                        "None"
                );
        final ComboBox q8box = new ComboBox(q8options);
        grid.add(q8box, 1, 8);

        Label q9 = new Label("On average, how many hours do you sleep on a school day?");
        grid.add(q9, 0, 9);

        Spinner q9box = new Spinner(0, 14, 8);
        q9box.setEditable(true);
        grid.add(q9box, 1, 9);

        Label q10 = new Label("How often do you revise for exams?");
        grid.add(q10, 0, 10);

        ObservableList<String> q10options =
                FXCollections.observableArrayList(
                        "Always revising",
                        "Several weeks ahead",
                        "A week ahead",
                        "Only a day or two ahead",
                        "I don't"
                );
        final ComboBox q10box = new ComboBox(q10options);
        grid.add(q10box, 1, 10);

        Label q11 = new Label("How often do you take breaks when studying?");
        grid.add(q11, 0, 11);

        ObservableList<String> q11options =
                FXCollections.observableArrayList(
                        "Frequently",
                        "Occasionally",
                        "Rarely"
                );
        final ComboBox q11box = new ComboBox(q11options);
        grid.add(q11box, 1, 11);

        Label q12 = new Label("Do you have free internet access at home?");
        grid.add(q12, 0, 12);

        ObservableList<String> q12options =
                FXCollections.observableArrayList(
                        "Yes",
                        "No"
                );
        final ComboBox q12box = new ComboBox(q12options);
        grid.add(q12box, 1, 12);

        Label q13 = new Label("Do you have a private tutor?");
        grid.add(q13, 0, 13);

        ObservableList<String> q13options =
                FXCollections.observableArrayList(
                        "Yes",
                        "No"
                );
        final ComboBox q13box = new ComboBox(q13options);
        grid.add(q13box, 1, 13);

        primaryStage.show();
    }
}
