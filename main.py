import flet as ft
import jdatetime
from datetime import timedelta

# بازه‌های زمانی
ROOF_SLOTS = [
    ("سانس ۱", "09:00 الی 10:45"),
    ("سانس ۲", "11:00 الی 12:45"),
    ("سانس ۳", "13:00 الی 14:45"),
    ("سانس ۴", "15:00 الی 16:45"),
    ("سانس ۵", "17:00 الی 18:45"),
    ("سانس ۶", "19:00 الی 24:00"),
]

POOL_SLOTS = [
    ("سانس ۱", "08:00 الی 09:30"),
    ("سانس ۲", "10:00 الی 11:30"),
    ("سانس ۳", "13:00 الی 14:30"),
    ("سانس ۴", "15:00 الی 16:30"),
    ("سانس ۵", "17:00 الی 18:30"),
    ("سانس ۶", "19:00 الی 20:30"),
    ("سانس ۷", "21:00 الی 22:30"),
]

BASE_DATE = jdatetime.date(1405, 7, 1)
ROOF_START_UNIT = 5

POOL_BASE_DATE = jdatetime.date(1405, 1, 2)
POOL_BASE_UNIT = 4

WEEK_DAYS = {
    0: "شنبه",
    1: "یکشنبه",
    2: "دوشنبه",
    3: "سه‌شنبه",
    4: "چهارشنبه",
    5: "پنج‌شنبه",
    6: "جمعه",
}

MONTH_NAMES = [
    "فروردین", "اردیبهشت", "خرداد",
    "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر",
    "دی", "بهمن", "اسفند"
]

YEAR_LIST = list(range(1400, 1411))


def get_days_in_jalali_month(year, month):
    if month <= 6:
        return 31
    elif month <= 11:
        return 30
    else:
        return 30 if jdatetime.date(year, 1, 1).isleap() else 29


def get_day_offset(target_date):
    return (target_date - BASE_DATE).days


def get_pool_day_offset(target_date):
    cur = POOL_BASE_DATE
    off = 0
    step = 1 if target_date >= POOL_BASE_DATE else -1
    while cur != target_date:
        if cur.weekday() != 6:
            off += step
        cur += timedelta(days=step)
    return off


def get_unit(start_unit, offset):
    return ((start_unit - 1 + offset) % 6) + 1


def main(page: ft.Page):
    page.title = "برنامه مشاعات ورونا"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#f0f4f8"
    page.scroll = "auto"
    page.window_width = 460
    page.window_height = 800
    page.rtl = True

    current_date = jdatetime.date.today()
    selected_unit = 1
    current_tab = "roof"

    is_syncing = False

    selected_year = current_date.year
    selected_month = current_date.month
    selected_day = current_date.day

    date_title = ft.Text(size=16, weight="bold", color="#0d47a1")
    slots_column = ft.Column(spacing=6)
    unit_buttons_row = ft.Row(alignment="center", spacing=6)

    # کانتینرهای نگهدارنده چرخ‌ها برای بازسازی بدون باگ
    day_box_content = ft.Container(alignment=ft.Alignment(0, 0))
    month_box_content = ft.Container(alignment=ft.Alignment(0, 0))
    year_box_content = ft.Container(alignment=ft.Alignment(0, 0))

    def make_wheel_box(title, inner_container, width=90):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(title, size=12, weight="bold", color="#1565c0"),
                    ft.Container(
                        content=inner_container,
                        height=100,
                        width=width,
                        border_radius=15,
                        bgcolor="#ffffff",
                        alignment=ft.Alignment(0, 0),
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=6,
                            color="#20000000",
                            offset=ft.Offset(0, 2),
                        ),
                        border=ft.border.all(1.2, "#bbdefb"),
                    ),
                ],
                horizontal_alignment="center",
                spacing=3,
            ),
            alignment=ft.Alignment(0, 0),
        )

    def make_picker_item(text):
        return ft.Container(
            content=ft.Text(text, size=14, weight="bold", color="#1a237e"),
            alignment=ft.Alignment(0, 0),
        )

    def on_day_change(e):
        nonlocal selected_day
        if is_syncing:
            return
        try:
            idx = int(e.data) if e.data is not None else 0
            selected_day = idx + 1
            apply_wheel_date()
        except Exception:
            pass

    def on_month_change(e):
        nonlocal selected_month
        if is_syncing:
            return
        try:
            idx = int(e.data) if e.data is not None else 0
            selected_month = idx + 1
            build_day_picker()
            apply_wheel_date()
        except Exception:
            pass

    def on_year_change(e):
        nonlocal selected_year
        if is_syncing:
            return
        try:
            idx = int(e.data) if e.data is not None else 0
            selected_year = YEAR_LIST[idx]
            build_day_picker()
            apply_wheel_date()
        except Exception:
            pass

    def build_day_picker():
        max_d = get_days_in_jalali_month(selected_year, selected_month)
        cur_idx = max(0, min(selected_day - 1, max_d - 1))
        day_box_content.content = ft.CupertinoPicker(
            item_extent=34,
            magnification=1.2,
            use_magnifier=True,
            squeeze=1.1,
            controls=[make_picker_item(str(d)) for d in range(1, max_d + 1)],
            selected_index=cur_idx,
            on_change=on_day_change,
        )

    def build_month_picker():
        cur_idx = max(0, min(selected_month - 1, len(MONTH_NAMES) - 1))
        month_box_content.content = ft.CupertinoPicker(
            item_extent=34,
            magnification=1.2,
            use_magnifier=True,
            squeeze=1.1,
            controls=[make_picker_item(m) for m in MONTH_NAMES],
            selected_index=cur_idx,
            on_change=on_month_change,
        )

    def build_year_picker():
        y_idx = YEAR_LIST.index(selected_year) if selected_year in YEAR_LIST else 5
        year_box_content.content = ft.CupertinoPicker(
            item_extent=34,
            magnification=1.2,
            use_magnifier=True,
            squeeze=1.1,
            controls=[make_picker_item(str(y)) for y in YEAR_LIST],
            selected_index=y_idx,
            on_change=on_year_change,
        )

    def apply_wheel_date():
        nonlocal current_date, is_syncing
        max_d = get_days_in_jalali_month(selected_year, selected_month)
        d = min(selected_day, max_d)
        try:
            new_d = jdatetime.date(selected_year, selected_month, d)
            current_date = new_d
            is_syncing = True
            update_view(rebuild_pickers=False)
            is_syncing = False
        except Exception as exc:
            print("خطا در تنظیم تاریخ:", exc)

    def sync_pickers_with_date():
        """همگام‌سازی کامل چرخه‌ها با تاریخ جاری با بازسازی کنترلرها"""
        nonlocal is_syncing, selected_year, selected_month, selected_day
        is_syncing = True
        selected_year = current_date.year
        selected_month = current_date.month
        selected_day = current_date.day

        build_year_picker()
        build_month_picker()
        build_day_picker()

        is_syncing = False

    roof_tab_btn = ft.Container(
        content=ft.Text("🌿 پشت بام", size=14, weight="bold", color="#ffffff"),
        bgcolor="#1565c0",
        padding=8,
        border_radius=10,
        alignment=ft.Alignment(0, 0),
        width=125,
    )
    pool_tab_btn = ft.Container(
        content=ft.Text("🏊‍♂️ استخر", size=14, weight="bold", color="#37474f"),
        bgcolor="#e0e0e0",
        padding=8,
        border_radius=10,
        alignment=ft.Alignment(0, 0),
        width=125,
    )

    def create_card(slot_name, time_str, unit_num, is_pool_friday=False):
        is_mine = (unit_num == selected_unit)

        if is_pool_friday:
            badge_bg = "#757575"
            badge_text = "هماهنگی با سرایدار"
            border_color = "#bdbdbd"
            bg_color = "#f5f5f5"
        elif is_mine:
            badge_bg = "#2e7d32"
            badge_text = f"⭐ نوبت شما (واحد {unit_num})"
            border_color = "#388e3c"
            bg_color = "#e8f5e9"
        else:
            badge_bg = "#1565c0"
            badge_text = f"واحد {unit_num}"
            border_color = "#90caf9"
            bg_color = "#ffffff"

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(slot_name, size=14, weight="bold", color="#212121"),
                            ft.Text(f"⏰ {time_str}", size=13, color="#424242", weight="w500"),
                        ],
                        spacing=10,
                        vertical_alignment="center",
                    ),
                    ft.Container(
                        content=ft.Text(badge_text, color="#ffffff", size=12, weight="bold"),
                        bgcolor=badge_bg,
                        padding=ft.Padding(left=10, right=10, top=5, bottom=5),
                        border_radius=12,
                    )
                ],
                alignment="spaceBetween",
            ),
            bgcolor=bg_color,
            padding=ft.Padding(left=12, right=12, top=8, bottom=8),
            border=ft.border.all(1.2, border_color),
            border_radius=8,
        )

    def on_unit_click(e):
        nonlocal selected_unit
        selected_unit = e.control.data
        render_unit_selector()
        update_view(rebuild_pickers=False)

    def render_unit_selector():
        unit_buttons_row.controls.clear()
        for u in range(1, 7):
            is_active = (u == selected_unit)
            btn = ft.Container(
                content=ft.Text(
                    f"واحد {u}",
                    size=12,
                    weight="bold",
                    color="#ffffff" if is_active else "#0d47a1",
                ),
                bgcolor="#1976d2" if is_active else "#bbdefb",
                border=ft.border.all(1.2, "#1565c0"),
                padding=ft.Padding(left=10, right=10, top=5, bottom=5),
                border_radius=8,
                data=u,
                on_click=on_unit_click,
            )
            unit_buttons_row.controls.append(btn)

    def update_view(rebuild_pickers=True):
        nonlocal current_date
        d_name = WEEK_DAYS[current_date.weekday()]
        m_name = MONTH_NAMES[current_date.month - 1]
        date_title.value = f"📅 {d_name} {current_date.day} {m_name} {current_date.year}"

        if rebuild_pickers:
            sync_pickers_with_date()

        is_friday = (current_date.weekday() == 6)
        slots_column.controls.clear()

        if current_tab == "roof":
            roof_tab_btn.bgcolor = "#1565c0"
            roof_tab_btn.content.color = "#ffffff"
            pool_tab_btn.bgcolor = "#e0e0e0"
            pool_tab_btn.content.color = "#37474f"

            roof_first = get_unit(ROOF_START_UNIT, get_day_offset(current_date))
            for i, slot in enumerate(ROOF_SLOTS):
                u_num = get_unit(roof_first, i)
                slots_column.controls.append(create_card(slot[0], slot[1], u_num))
        else:
            pool_tab_btn.bgcolor = "#1565c0"
            pool_tab_btn.content.color = "#ffffff"
            roof_tab_btn.bgcolor = "#e0e0e0"
            roof_tab_btn.content.color = "#37474f"

            pool_first = get_unit(POOL_BASE_UNIT, get_pool_day_offset(current_date))

            if is_friday:
                slots_column.controls.append(
                    ft.Container(
                        content=ft.Text(
                            "⚠️ جمعه‌ها استخر صرفاً با هماهنگی قبلی با سرایدار قابل استفاده است.",
                            color="#b71c1c",
                            size=12,
                            weight="bold",
                        ),
                        bgcolor="#ffebee",
                        padding=8,
                        border_radius=8,
                        border=ft.border.all(1, "#ef9a9a"),
                    )
                )
                for slot in POOL_SLOTS:
                    slots_column.controls.append(
                        create_card(slot[0], slot[1], None, is_pool_friday=True)
                    )
            else:
                for i, slot in enumerate(POOL_SLOTS):
                    u_num = get_unit(pool_first, i)
                    slots_column.controls.append(create_card(slot[0], slot[1], u_num))

        page.update()

    def change_date(days):
        nonlocal current_date
        current_date += timedelta(days=days)
        update_view(rebuild_pickers=True)

    def go_today(e):
        nonlocal current_date
        current_date = jdatetime.date.today()
        update_view(rebuild_pickers=True)

    def set_tab(tab_name):
        nonlocal current_tab
        current_tab = tab_name
        update_view(rebuild_pickers=False)

    roof_tab_btn.on_click = lambda e: set_tab("roof")
    pool_tab_btn.on_click = lambda e: set_tab("pool")

    btn_prev = ft.Container(
        content=ft.Text("⬅️ روز قبل", size=12, weight="bold", color="#ffffff"),
        bgcolor="#1e88e5",
        padding=ft.Padding(left=10, right=10, top=5, bottom=5),
        border_radius=8,
        on_click=lambda e: change_date(-1),
    )
    btn_today = ft.Container(
        content=ft.Text("امروز", size=12, weight="bold", color="#0d47a1"),
        bgcolor="#bbdefb",
        border=ft.border.all(1, "#1976d2"),
        padding=ft.Padding(left=10, right=10, top=5, bottom=5),
        border_radius=8,
        on_click=go_today,
    )
    btn_next = ft.Container(
        content=ft.Text("روز بعد ➡️", size=12, weight="bold", color="#ffffff"),
        bgcolor="#1e88e5",
        padding=ft.Padding(left=10, right=10, top=5, bottom=5),
        border_radius=8,
        on_click=lambda e: change_date(1),
    )

    render_unit_selector()
    sync_pickers_with_date()

    wheels_row = ft.Row(
        controls=[
            make_wheel_box("روز", day_box_content, width=80),
            make_wheel_box("ماه", month_box_content, width=120),
            make_wheel_box("سال", year_box_content, width=95),
        ],
        alignment="center",
        spacing=8,
    )

    page.add(
        ft.Row(
            [ft.Text("🏢 برنامه مشاعات ورونا", size=20, weight="bold", color="#0d47a1")],
            alignment="center",
        ),
        ft.Divider(height=1, thickness=1),
        ft.Text("واحد خود را انتخاب کنید:", size=12, weight="bold", color="#37474f"),
        unit_buttons_row,
        ft.Container(height=4),
        ft.Container(
            content=ft.Column([
                wheels_row,
                ft.Container(content=date_title, alignment=ft.alignment.center),
                ft.Row([btn_prev, btn_today, btn_next], alignment="center", spacing=8),
            ], spacing=6),
            bgcolor="#e3f2fd",
            padding=10,
            border_radius=12,
            border=ft.border.all(1, "#90caf9"),
        ),
        ft.Container(height=6),
        ft.Row([roof_tab_btn, pool_tab_btn], alignment="center", spacing=8),
        ft.Container(height=4),
        slots_column,
    )

    update_view(rebuild_pickers=False)

if __name__ == "__main__":
    try:
        ft.run(main)
    except AttributeError:
        try:
            ft.app(target=main)
        except AttributeError:
            import flet.app as flet_app

            ft.app(target=main)
   
