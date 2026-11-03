struct AbstractTask {
    virtual void run() = 0;
    virtual ~AbstractTask() = default;
};

struct ConcreteTask : AbstractTask {
    void run() override {}
};

int main() {
    ConcreteTask task;
    task.run();
    return 0;
}
