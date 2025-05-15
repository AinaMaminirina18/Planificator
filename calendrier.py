from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout

import calendar
from datetime import datetime


class CalendarWidget(BoxLayout):
    def __init__(self, year, month, data, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.dialog = None
        self.year = year
        self.month = month
        self.traitements_par_jour = data

        self.grid = MDGridLayout(cols=7, adaptive_height=True, padding=10, spacing=5)
        self.grid.pos_hint = {'center_x': .76, 'center_y': .5}
        self.add_widget(self.grid)

        self.build_calendar()

    def build_calendar(self):
        self.grid.clear_widgets()
        calendar_data = calendar.monthcalendar(self.year, self.month)
        for week in calendar_data:
            for day in week:
                card = MDCard(
                    size_hint=(None, None),
                    size=("130dp", "110dp"),
                    orientation="vertical",
                    padding=5,
                    md_bg_color= '#A5D8FD',
                    ripple_behavior=True,
                )

                if day != 0:
                    date_str = f"{self.year}-{self.month:02d}-{day:02d}"
                    date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    card.bind(on_release=self.make_popup_callback(date))

                    card.add_widget(MDLabel(
                        text=str(day),
                        halign="left",
                        font_style="Subtitle1"
                    ))

                    traitements = self.traitements_par_jour.get(date, [])
                    for t in traitements[:2]:
                        color = (1, 0, 0, 1) if t['etat'] == "Effectué" else (0, 0, 0, 1)
                        card.add_widget(MDLabel(
                            text=f"- {t['traitement']}",
                            theme_text_color="Custom",
                            text_color=color,
                            font_style="Caption",
                            halign="left"
                        ))

                    if len(traitements) > 2:
                        voir_plus = MDLabel(
                            text="... Voir plus",
                            font_style="Caption",
                            halign="right",
                            theme_text_color="Custom",
                            text_color=(0.2, 0.4, 1, 1)
                        )
                        voir_plus.bind(on_touch_down=lambda inst, touch, d=date:
                                       self.show_dialog(d) if inst.collide_point(*touch.pos) else None)
                        card.add_widget(voir_plus)

                self.grid.add_widget(card)

    def make_popup_callback(self, date_str):
        def callback(*_):
            self.show_dialog(date_str)
        return callback

    def show_dialog(self, date_str):
        traitements = self.traitements_par_jour.get(date_str, [])

        if self.dialog:
            self.dialog.dismiss()

        from kivymd.uix.boxlayout import MDBoxLayout
        from kivymd.uix.label import MDLabel

        layout = MDBoxLayout(orientation='vertical', spacing=5, padding=5, adaptive_height=True)

        if traitements:
            for t in traitements:
                color = (1, 0, 0, 1) if t["etat"] == "Effectué" else (0, 0, 0, 1)
                layout.add_widget(MDLabel(
                    text=f"- {t['traitement']} ({t['etat']})",
                    theme_text_color="Custom",
                    text_color=color,
                    halign="left",
                    size_hint_y=None,
                    height=25
                ))
        else:
            layout.add_widget(MDLabel(
                text="Aucun traitement.",
                halign="center",
                size_hint_y=None,
                height=25
            ))

        self.dialog = MDDialog(
            title=f"Traitements le {date_str}",
            type="custom",
            content_cls=layout,
            buttons=[
                MDFlatButton(text="Fermer", on_release=lambda x: self.dialog.dismiss())
            ],
        )
        self.dialog.open()