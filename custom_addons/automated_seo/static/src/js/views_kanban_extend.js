/** @odoo-module */
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { registry } from '@web/core/registry';
import { kanbanView } from '@web/views/kanban/kanban_view';
export class ViewsKanbanController extends KanbanController {
   setup() {
       super.setup();
   }
   OnCreatePageClick() {
       this.actionService.doAction({
          type: 'ir.actions.act_window',
          res_model: 'automated_seo.view_create_wizard',
          name:'Create Page',
          view_mode: 'form',
          view_type: 'form',
          views: [[false, 'form']],
          target: 'new',
          res_id: false,
      });
   }
}
registry.category("views").add("button_in_kanban", {
   ...kanbanView,
   Controller: ViewsKanbanController,
   buttonTemplate: "automated_seo.view.KanbanView.Buttons",
});