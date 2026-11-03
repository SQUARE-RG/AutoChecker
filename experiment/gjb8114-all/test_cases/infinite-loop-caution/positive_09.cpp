int runUntilDone() {
    bool taskPending = true;
    int processed = 0;
    while (taskPending) {
        ++processed;
        if (processed >= 4) {
            taskPending = false;
        }
    }
    return processed;
}

int main() {
    return runUntilDone();
}
