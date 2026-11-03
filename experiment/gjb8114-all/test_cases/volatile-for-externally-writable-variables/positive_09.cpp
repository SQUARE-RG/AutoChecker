#include <cstdint>

using EventCallback = void (*)();

// 该函数由外部线程注册为回调，并在另一个线程中异步调用。
void on_external_event()
{
    static volatile std::uint32_t event_counter = 0;
    event_counter = event_counter + 1;
}

EventCallback get_callback()
{
    return &on_external_event;
}
