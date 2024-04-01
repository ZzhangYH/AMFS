--Copyright (C) 2024 Yuhan Zhang - All Rights Reserved
--
--This file is part of AMFS, which is distributed under the terms of the GPLv3 License.
--See the file LICENSE at the top level directory of this distribution for details.

DROP TABLE IF EXISTS Submission;
DROP TABLE IF EXISTS TestCase;
DROP TABLE IF EXISTS Attempt;
DROP TABLE IF EXISTS Feedback;
DROP TABLE IF EXISTS FeedbackSelection;

CREATE TABLE Submission (
    sm_id VARCHAR PRIMARY KEY,
    sm_mark FLOAT
);

CREATE TABLE TestCase (
    tc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tc_name VARCHAR NOT NULL,
    tc_mark FLOAT NOT NULL,
    tc_input VARCHAR NOT NULL
);

CREATE TABLE Attempt (
    at_id INTEGER PRIMARY KEY AUTOINCREMENT,
    at_code INTEGER NOT NULL,
    at_mark FLOAT NOT NULL,
    at_output VARCHAR NOT NULL,
    sm_id VARCHAR NOT NULL,
    tc_id INTEGER NOT NULL,
    FOREIGN KEY (sm_id) REFERENCES Submission (sm_id),
    FOREIGN KEY (tc_id) REFERENCES TestCase (tc_id)
);

CREATE TABLE Feedback (
    fb_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fb_content VARCHAR NOT NULL
);

CREATE TABLE FeedbackSelection (
    fs_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fb_id INTEGER NOT NULL,
    tc_id INTEGER NOT NULL,
    FOREIGN KEY (fb_id) REFERENCES Feedback (fb_id),
    FOREIGN KEY (tc_id) REFERENCES TestCase (tc_id)
);
