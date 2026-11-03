#include <functional>
#include <iostream>

enum class Result { ok, null_event };

using Handler = std::function<Result(const char*)>;

Result dispatch(Handler handler, const char* event) {
    return handler(event);
}

int main() {
    Handler handler = [](const char* event) {
        if (event == nullptr) {
            std::cerr << "null event\n";
            return Result::null_event;
        }
        std::cout << event << "\n";
        return Result::ok;
    };
    Result result = dispatch(handler, nullptr);
    return result == Result::ok ? 0 : 1;
}
